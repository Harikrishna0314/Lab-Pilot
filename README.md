CampusLab Agent — AI-Powered Computer Laboratory Assistant
Python 3.11 Flask PostgreSQL Docker License: MIT

CampusLab Agent is a production-quality, full-stack web application designed for universities and academic institutions. It enables students, faculty, and lab administrators to manage computer laboratory reservations seamlessly using natural language chat commands.

🌟 Key Features
🤖 AI Natural Language Chat Assistant
Translate conversational requests directly into backend API executions.
Supported natural language queries:
"I need Lab A tomorrow from 10 to 12."
"Book System 15."
"Cancel my booking."
"Move my booking to Friday."
"Show my reservations."
💻 Laboratory & Real-Time Seat Tracking
Interactive lab seat matrix showing live statuses: Available, Reserved, or Faulty.
Conflict resolution logic automatically detects overlapping slots, enforces lab opening hours, and suggests alternative available seats or time windows.
🔐 Authentication & Role-Based Authorization
JWT (JSON Web Tokens) authentication.
Three user roles with tailored interfaces and permissions:
Student: Book systems, view personal reservations, report equipment faults.
Faculty: Book systems, manage project reservations.
Lab Admin: Full management dashboard, create new labs, disable faulty equipment, mark repairs, view occupancy analytics.
⚠️ Equipment Fault Reporting
Students & faculty can log hardware/network issues (Keyboard, Mouse, Monitor, Network, Power).
Automatically marks reported systems as FAULTY to prevent reservations until repaired.
🏗️ Project Architecture
CampusLab-Agent/
│
├── app.py                     # Application factory & page routes
├── config.py                  # Environment configurations (Dev, Test, Prod)
├── models.py                 # SQLAlchemy ORM database models
├── database.sql               # PostgreSQL schema & seed script
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── API_DOCUMENTATION.md       # OpenAPI-style REST API docs
│
├── services/                  # Business logic layer
│   ├── auth_service.py        # Hashing, authentication, JWT tokens
│   ├── lab_service.py         # Lab CRUD, real-time seat availability
│   ├── booking_service.py     # Conflict detection, suggestions, booking logic
│   └── fault_service.py       # Fault logging & maintenance management
│
├── ai/                        # Natural Language Processing layer
│   └── assistant.py           # Intent extraction & function calling dispatcher
│
├── routes/                    # REST API endpoints (Blueprints)
│   ├── auth.py                # /api/register, /api/login, /api/me
│   ├── labs.py                # /api/labs
│   ├── systems.py             # /api/systems
│   ├── bookings.py            # /api/book, /api/booking/<id>, /api/bookings
│   ├── faults.py              # /api/fault, /api/faults
│   └── ai_chat.py            # /api/chat
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Glassmorphism layout & navbar
│   ├── login.html             # User login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # User dashboard & metrics
│   ├── chat.html              # AI Assistant chat view
│   ├── bookings.html          # Personal reservations view
│   ├── labs.html              # Interactive seat grid view
│   ├── admin.html             # Admin analytics & occupancy charts
│   └── faults.html            # Maintenance & fault reporting
│
├── static/                    # Frontend styling & JavaScript
│   ├── css/style.css          # Custom dark glassmorphism stylesheet
│   └── js/main.js             # API wrapper & frontend logic
│
├── docker/                    # Dockerization container files
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .github/workflows/         # CI/CD Workflows
│   └── ci.yml                 # GitHub Actions automated testing
│
└── tests/                     # PyTest automated unit & integration test suite
    ├── conftest.py
    ├── test_auth.py
    ├── test_bookings.py
    └── test_ai.py
🛢️ Database ER Diagram (PostgreSQL)
+--------------------+        +--------------------+
|       USERS        |        |        LABS        |
+--------------------+        +--------------------+
| id (PK)            |        | id (PK)            |
| name               |        | name               |
| email (UNIQUE)     |        | capacity           |
| password_hash      |        | open_time          |
| role               |        | close_time         |
| created_at         |        | description        |
+---------+----------+        +---------+----------+
          |                             |
          | 1                           | 1
          |                             |
          | N                           | N
+---------v----------+        +---------v----------+
|      BOOKINGS      |        |      SYSTEMS       |
+--------------------+        +--------------------+
| id (PK)            | N    1 | id (PK)            |
| user_id (FK)       +--------+ lab_id (FK)        |
| system_id (FK)     |        | system_number      |
| booking_date       |        | status             |
| start_time         |        +---------+----------+
| end_time           |                  |
| status             |                  | 1
+--------------------+                  |
                                        | N
                              +---------v----------+
                              |   FAULT_REPORTS    |
                              +--------------------+
                              | id (PK)            |
                              | system_id (FK)     |
                              | reported_by (FK)   |
                              | issue_type         |
                              | description        |
                              | status             |
                              +--------------------+
⚡ Quick Start & Installation Guide
Prerequisites
Python 3.11+
PostgreSQL 15+ (or Docker)
Git
Local Setup (Virtualenv)
Clone Repository & Navigate:

git clone https://github.com/campuslab/campuslab-agent.git
cd CampusLab-Agent
Create Virtual Environment & Install Dependencies:

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
Configure Environment Variables: Create a .env file in the root folder:

FLASK_ENV=development
SECRET_KEY=super-secret-key
JWT_SECRET_KEY=jwt-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/campuslab_db
OPENAI_API_KEY=your_openai_api_key_here
Initialize Database:

psql -U postgres -d campuslab_db -f database.sql
Run Development Server:

python app.py
Open your browser at http://localhost:5000.

🐳 Docker Deployment
To launch the full application with PostgreSQL using Docker Compose:

cd docker
docker-compose up --build
Access the application at http://localhost:5000.

🧪 Running Automated Tests
Run the PyTest test suite:

pytest -v tests/
🔮 Future Enhancements
SSO / SAML Integration: OAuth2 / Google Workspace login for university students.
WebSocket Real-time Updates: Real-time push updates for live seat booking matrix using Flask-SocketIO.
Voice Input Assistant: Native speech-to-text integration for accessibility.
QR Code Scanning: QR check-in at physical computer workstations.
