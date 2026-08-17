CampusLab Agent — AI-Powered Computer Laboratory Assistant

CampusLab Agent is an AI-powered, full-stack web application designed for universities and academic institutions to simplify computer laboratory management. It enables students, faculty, and lab administrators to reserve computer systems, check real-time seat availability, report equipment faults, and manage laboratory resources through a user-friendly interface. The platform also includes a natural-language AI assistant that allows users to perform actions using simple conversational commands such as “Book System 15”, “Cancel my booking”, or “Show my reservations.”

🌟 Key Features
🤖 AI Natural Language Assistant – Converts conversational requests into appropriate backend actions.
💻 Real-Time Seat Tracking – Displays computer systems as Available, Reserved, or Faulty.
📅 Smart Reservation System – Detects booking conflicts and suggests alternative seats or time slots.
🔐 JWT Authentication – Provides secure login and role-based access.
👥 Role-Based Access Control – Separate features and permissions for Students, Faculty, and Lab Administrators.
⚠️ Equipment Fault Reporting – Users can report issues with keyboards, monitors, network, power, and other equipment.
📊 Admin Dashboard – Allows administrators to manage laboratories, faulty systems, reservations, and occupancy analytics.
🐳 Docker Support – Supports containerized deployment using Docker and Docker Compose.
🧪 Automated Testing – Includes PyTest-based unit and integration tests.
🔄 CI/CD – GitHub Actions workflow for automated testing and development.
🛠️ Technology Stack
Python 3.11
Flask
PostgreSQL
SQLAlchemy
JWT Authentication
OpenAI API
HTML, CSS, JavaScript
Docker & Docker Compose
PyTest
GitHub Actions
🏗️ Project Architecture

The application follows a modular architecture with separate layers for authentication, laboratory management, booking operations, fault management, AI processing, and REST APIs. PostgreSQL is used for persistent data storage, while Flask handles the backend and web application. The AI assistant processes natural-language requests and dispatches them to the appropriate backend services.

🚀 Future Enhancements
University SSO/SAML authentication
Real-time updates using WebSockets
Voice-based AI assistant
QR-code-based laboratory check-in
AI-based laboratory usage prediction
Automated email and mobile notifications
Advanced occupancy and usage analytics
👨‍💻 Author

Harikrishna
B.Tech — Artificial Intelligence & Data Science

CampusLab Agent combines AI, web development, database management, and automation to create a smarter and more efficient computer laboratory management system for academic institutions.
