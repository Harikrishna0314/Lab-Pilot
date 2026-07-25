import os
import json
import re
from datetime import datetime, timedelta, date
from openai import OpenAI
from services import booking_service, lab_service, fault_service
from models import Lab, System, Booking

client = None
if os.getenv("OPENAI_API_KEY"):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception:
        client = None

SYSTEM_PROMPT = """
You are CampusLab Agent, an intelligent lab booking AI assistant.
Your goal is to parse user chat messages to perform computer laboratory booking, modification, cancellation, checking availability, viewing bookings, or reporting faulty systems.

Today's date is: {today_date} ({day_of_week}).

Return a valid JSON object strictly matching this schema:
{
  "intent": "book" | "cancel" | "modify" | "view" | "check_availability" | "report_fault" | "unknown",
  "lab_name": "Lab A - AI & Data Science" | "Lab B - Software Engineering" | "Lab C - Hardware & Networking" | null,
  "system_number": integer or null,
  "booking_date": "YYYY-MM-DD" or null,
  "start_time": "HH:MM" (24h) or null,
  "end_time": "HH:MM" (24h) or null,
  "booking_id": integer or null,
  "issue_type": "keyboard" | "mouse" | "monitor" | "network" | "power" | "other" | null,
  "description": string or null,
  "response_message": "A friendly conversational response summarizing what is being executed or asking for missing info."
}
"""

def parse_with_heuristics(user_message, today_dt=None):
    """Fallback rule-based NLP parser when OpenAI API key is not available"""
    if not today_dt:
        today_dt = date.today()

    msg_lower = user_message.lower()
    intent = "unknown"
    lab_name = None
    system_number = None
    booking_date = today_dt.strftime("%Y-%m-%d")
    start_time = None
    end_time = None
    booking_id = None
    issue_type = None
    description = None

    # Detect Lab Name
    if "lab a" in msg_lower:
        lab_name = "Lab A - AI & Data Science"
    elif "lab b" in msg_lower:
        lab_name = "Lab B - Software Engineering"
    elif "lab c" in msg_lower:
        lab_name = "Lab C - Hardware & Networking"

    # Detect System Number
    sys_match = re.search(r'system\s*(?:no\.?|number|id)?\s*(\d+)', msg_lower)
    if sys_match:
        system_number = int(sys_match.group(1))

    # Detect Date
    if "tomorrow" in msg_lower:
        booking_date = (today_dt + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "friday" in msg_lower:
        days_ahead = (4 - today_dt.weekday() + 7) % 7
        if days_ahead == 0: days_ahead = 7
        booking_date = (today_dt + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    elif "today" in msg_lower:
        booking_date = today_dt.strftime("%Y-%m-%d")

    # Detect Times (e.g. "from 10 to 12" or "10am to 12pm" or "14:00 to 16:00")
    time_match = re.search(r'(?:from\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:to|-)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', msg_lower)
    if time_match:
        s_h, s_m, s_ap, e_h, e_m, e_ap = time_match.groups()
        s_h = int(s_h)
        s_m = int(s_m) if s_m else 0
        e_h = int(e_h)
        e_m = int(e_m) if e_m else 0

        if s_ap == 'pm' and s_h < 12: s_h += 12
        if e_ap == 'pm' and e_h < 12: e_h += 12
        if not s_ap and not e_ap and s_h < 8 and e_h <= 12: # Assumed AM/PM heuristics
            s_h += 12
            e_h += 12

        start_time = f"{s_h:02d}:{s_m:02d}"
        end_time = f"{e_h:02d}:{e_m:02d}"

    # Detect Intents
    if any(k in msg_lower for k in ["cancel"]):
        intent = "cancel"
        id_match = re.search(r'booking\s*#?(\d+)', msg_lower)
        if id_match:
            booking_id = int(id_match.group(1))
    elif any(k in msg_lower for k in ["move", "modify", "reschedule", "change"]):
        intent = "modify"
    elif any(k in msg_lower for k in ["show", "view", "my reservations", "my bookings", "list"]):
        intent = "view"
    elif any(k in msg_lower for k in ["available", "free seats", "check"]):
        intent = "check_availability"
    elif any(k in msg_lower for k in ["report", "fault", "issue", "broken", "damaged"]):
        intent = "report_fault"
        for issue in ["keyboard", "mouse", "monitor", "network", "power"]:
            if issue in msg_lower:
                issue_type = issue
                break
        if not issue_type:
            issue_type = "other"
        description = user_message
    elif any(k in msg_lower for k in ["book", "reserve", "need"]):
        intent = "book"

    return {
        "intent": intent,
        "lab_name": lab_name or "Lab A - AI & Data Science",
        "system_number": system_number,
        "booking_date": booking_date,
        "start_time": start_time or "10:00",
        "end_time": end_time or "11:00",
        "booking_id": booking_id,
        "issue_type": issue_type,
        "description": description,
        "response_message": "Processing your natural language request..."
    }

def process_chat_message(user_id, user_message):
    today = date.today()
    parsed = None

    if client:
        try:
            prompt = SYSTEM_PROMPT.format(today_date=today.strftime("%Y-%m-%d"), day_of_week=today.strftime("%A"))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            parsed = json.loads(response.choices[0].message.content)
        except Exception as e:
            parsed = parse_with_heuristics(user_message, today)
    else:
        parsed = parse_with_heuristics(user_message, today)

    intent = parsed.get("intent")
    
    # 1. INTENT: BOOK
    if intent == "book":
        lab_name = parsed.get("lab_name") or "Lab A - AI & Data Science"
        lab = Lab.query.filter(Lab.name.ilike(f"%{lab_name}%")).first() or Lab.query.first()
        if not lab:
            return {"status": "error", "message": "No laboratories found in database."}

        booking_data, err, conflict = booking_service.create_booking(
            user_id=user_id,
            lab_id=lab.id,
            system_number=parsed.get("system_number"),
            booking_date_str=parsed.get("booking_date"),
            start_time_str=parsed.get("start_time"),
            end_time_str=parsed.get("end_time")
        )
        if err:
            msg = f"❌ {err}"
            if conflict:
                if conflict.get("alternative_seats"):
                    msg += f"\n💡 Suggested Available Systems in {lab.name}: System #{', System #'.join(map(str, conflict['alternative_seats'][:5]))}"
                if conflict.get("alternative_timings"):
                    times = [f"{t['start_time']}-{t['end_time']}" for t in conflict['alternative_timings']]
                    msg += f"\n⏰ Suggested Alternative Timings: {', '.join(times)}"
            return {"status": "conflict", "message": msg, "data": conflict}

        return {
            "status": "success",
            "message": f"🎉 Successfully booked System #{booking_data['system_number']} in {booking_data['lab_name']} for {booking_data['booking_date']} ({booking_data['start_time']} - {booking_data['end_time']}). Booking ID: #{booking_data['id']}",
            "booking": booking_data
        }

    # 2. INTENT: CANCEL
    elif intent == "cancel":
        booking_id = parsed.get("booking_id")
        if not booking_id:
            # find latest user booking
            user_bookings = booking_service.get_user_bookings(user_id=user_id, status='active', upcoming_only=True)
            if not user_bookings:
                return {"status": "error", "message": "You don't have any active upcoming bookings to cancel."}
            booking_id = user_bookings[0]['id']

        cancelled_data, err = booking_service.cancel_booking(booking_id=booking_id, user_id=user_id)
        if err:
            return {"status": "error", "message": f"❌ {err}"}
        return {"status": "success", "message": f"✅ Booking #{booking_id} has been successfully cancelled.", "booking": cancelled_data}

    # 3. INTENT: MODIFY
    elif intent == "modify":
        booking_id = parsed.get("booking_id")
        if not booking_id:
            user_bookings = booking_service.get_user_bookings(user_id=user_id, status='active', upcoming_only=True)
            if not user_bookings:
                return {"status": "error", "message": "You don't have any active upcoming bookings to modify."}
            booking_id = user_bookings[0]['id']

        modified_data, err, conflict = booking_service.modify_booking(
            booking_id=booking_id,
            user_id=user_id,
            new_date_str=parsed.get("booking_date"),
            new_start_str=parsed.get("start_time"),
            new_end_str=parsed.get("end_time"),
            new_system_number=parsed.get("system_number")
        )
        if err:
            return {"status": "conflict", "message": f"❌ {err}", "data": conflict}
        return {"status": "success", "message": f"✏️ Booking #{booking_id} updated successfully to {modified_data['booking_date']} ({modified_data['start_time']} - {modified_data['end_time']}).", "booking": modified_data}

    # 4. INTENT: VIEW
    elif intent == "view":
        bookings = booking_service.get_user_bookings(user_id=user_id)
        if not bookings:
            return {"status": "success", "message": "You currently have no lab reservations.", "bookings": []}
        
        b_list = "\n".join([f"• Booking #{b['id']}: {b['lab_name']} (Sys #{b['system_number']}) on {b['booking_date']} ({b['start_time']}-{b['end_time']}) - Status: {b['status'].upper()}" for b in bookings[:5]])
        return {"status": "success", "message": f"📋 Your Reservations:\n{b_list}", "bookings": bookings}

    # 5. INTENT: CHECK AVAILABILITY
    elif intent == "check_availability":
        labs = lab_service.get_all_labs()
        lab_summary = "\n".join([f"• {l['name']}: {l['available_systems']}/{l['capacity']} systems currently free ({l['open_time']} - {l['close_time']})" for l in labs])
        return {"status": "success", "message": f"💻 Real-time Seat Availability:\n{lab_summary}", "labs": labs}

    # 6. INTENT: REPORT FAULT
    elif intent == "report_fault":
        sys_num = parsed.get("system_number")
        if not sys_num:
            return {"status": "error", "message": "Please specify which system number is faulty (e.g. 'System 15')."}
        
        sys_obj = System.query.filter_by(system_number=sys_num).first()
        if not sys_obj:
            return {"status": "error", "message": f"System #{sys_num} not found."}

        report_data, err = fault_service.report_fault(
            system_id=sys_obj.id,
            reported_by=user_id,
            issue_type=parsed.get("issue_type") or "other",
            description=parsed.get("description") or f"Fault report for System #{sys_num}"
        )
        if err:
            return {"status": "error", "message": f"❌ {err}"}

        return {"status": "success", "message": f"⚠️ Fault report submitted for System #{sys_num} ({report_data['issue_type'].title()} issue). System marked as FAULTY.", "fault_report": report_data}

    else:
        return {
            "status": "unknown",
            "message": "I didn't quite catch that. Try asking something like:\n• 'I need Lab A tomorrow from 10 to 12'\n• 'Book System 15'\n• 'Cancel my booking'\n• 'Move my booking to Friday'\n• 'Show my reservations'"
        }
