from models import db, FaultReport, System

def report_fault(system_id, reported_by, issue_type, description=""):
    allowed_issues = ['keyboard', 'mouse', 'monitor', 'network', 'power', 'other']
    if issue_type.lower() not in allowed_issues:
        return None, f"Invalid issue type. Must be one of: {', '.join(allowed_issues)}"

    system = System.query.get(system_id)
    if not system:
        return None, "System not found."

    report = FaultReport(
        system_id=system_id,
        reported_by=reported_by,
        issue_type=issue_type.lower(),
        description=description,
        status='open'
    )
    
    # Automatically mark system as faulty
    system.status = 'faulty'
    
    db.session.add(report)
    db.session.commit()
    
    return report.to_dict(), None

def get_fault_reports(status=None, lab_id=None):
    query = FaultReport.query
    if status:
        query = query.filter_by(status=status)
    
    reports = query.order_by(FaultReport.created_at.desc()).all()
    if lab_id:
        reports = [r for r in reports if r.system and r.system.lab_id == int(lab_id)]

    return [r.to_dict() for r in reports]

def update_fault_status(report_id, status):
    if status not in ['open', 'in_progress', 'repaired']:
        return None, "Invalid status. Must be 'open', 'in_progress', or 'repaired'."

    report = FaultReport.query.get(report_id)
    if not report:
        return None, "Fault report not found."

    report.status = status
    
    # If marked as repaired, make system available again if no other open faults exist for it
    if status == 'repaired' and report.system:
        other_open_faults = FaultReport.query.filter(
            FaultReport.system_id == report.system_id,
            FaultReport.id != report_id,
            FaultReport.status.in_(['open', 'in_progress'])
        ).count()
        if other_open_faults == 0:
            report.system.status = 'available'

    db.session.commit()
    return report.to_dict(), None
