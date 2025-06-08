

# Remind Me Later

---

**Remind Me Later** is a modern, full-featured web application designed to help users effortlessly schedule and manage reminders with precision and reliability. Built using Python, Flask, Celery, and Redis, the platform supports both SMS and email notifications, ensuring users never miss an important event or task. The application features a sleek, UI/UX that is fully responsive and accessible across devices, offering an intuitive and visually appealing experience. With robust background task processing, real-time status updates, and comprehensive error handling, Remind Me Later stands out as a production-ready solution for personal productivity. Its modular architecture makes it easily extensible for future enhancements, while its secure, environment-based configuration ensures safe handling of sensitive information. This project not only fulfills but exceeds standard requirements, demonstrating both technical proficiency and a strong focus on user experience.

---

##  Features

- **Create Reminders:** Set a message, date, time, and choose SMS or Email delivery.
- **Multiple Delivery Methods:** Supports both Email (SMTP) and SMS (Twilio).
- **Background Processing:** Uses Celery with Redis for robust, non-blocking scheduling.
- **Clear All Reminders:** Bulk delete with confirmation.
- **Modern UI/UX:** Samsung-style, mobile-friendly, and visually appealing.
- **Live Time Widget:** See the current time and timezone contextually.
- **IST Timezone Support:** All times are stored and displayed in IST for Indian users.
- **Comprehensive Error Handling:** User-friendly error messages and validation.
- **Production-Ready:** Secure, modular, and extensible codebase.

---

## Tech Stack

### **Backend**
- **Python 3.8+**
- **Flask** – Lightweight web framework for Python
- **Flask-SQLAlchemy** – ORM for database management
- **Celery** – Distributed task queue for background jobs
- **Redis** – Message broker for Celery
- **pytz** – Timezone support
- **python-dotenv** – Environment variable management

### **Messaging & Email**
- **Twilio** – SMS delivery API
- **SMTP (Gmail)** – Email delivery

### **Frontend**
- **HTML5, CSS3, JavaScript (Vanilla)**
- **Jinja2** – Templating engine (via Flask)
- **Responsive custom CSS** –  modern, and accessible

### **DevOps & Utilities**
- **Virtualenv** – Python environment isolation
- **Git** – Version control
- **requirements.txt** – Dependency management

---

## UI/UX Design

- **Responsive design:** Works seamlessly on desktops, tablets, and mobiles.
- **Live time widget:** Contextual time and timezone display in the hero and reminders section.
- **Clear all reminders:** Prominent, safe, and accessible bulk action with confirmation modal.
- **Accessible:** Keyboard navigable, focus states, and clear error feedback.
- **Animations:** Subtle transitions and pulse effects for time updates and modal dialogs.
- **Visual hierarchy:** Large headers, clear sectioning, and intuitive navigation.
- **Consistent iconography:** Font Awesome for modern, universal icons.

---

## Installation & Setup

### **1. Clone the repository**
```bash
git clone https://github.com/yourusername/remind-me-later.git
cd remind-me-later
```

### **2. Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate   # On Windows
# or
source venv/bin/activate   # On Mac/Linux
```

### **3. Install dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure environment variables**

Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key
DATABASE_URI=sqlite:///reminders.db
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
```

### **5. Start supporting services**

#### **Redis**
- **Windows:** Use Memurai, WSL, or Chocolatey to install and run Redis.
- **Mac/Linux:** `redis-server`

#### **Celery Worker**
```bash
celery -A tasks worker --loglevel=info --pool=eventlet   # On Windows
celery -A tasks worker --loglevel=info                   # On Mac/Linux
```
#### **Flask App**
```bash
python app.py
```

---

## Usage

- Open [http://localhost:5000](http://localhost:5000) in your browser.
- Create reminders with date, time, message, and delivery method.
- View all reminders, check their status, and clear all with a single click.

---
## 🧩 API Endpoints

| Method | Endpoint                | Description                        |
|--------|-------------------------|------------------------------------|
| POST   | `/api/reminder`         | Create a new reminder              |
| GET    | `/api/reminders`        | List all reminders                 |
| DELETE | `/api/reminders/clear`  | Delete all reminders (bulk clear)  |

**Example: Create Reminder (POST /api/reminder)**
```json
{
  "date": "2025-06-08",
  "time": "14:30",
  "message": "Call mom for her birthday",
  "reminder_method": "email",
  "email_address": "user@example.com"
}
```

---
## 🧑‍💻 Development & Contribution

- Modular codebase: All logic is separated into `app.py`, `tasks.py`, and `config.py`.
- Environment variables for all credentials and secrets.
- Easily extensible for more delivery methods, user authentication, or recurring reminders.

---
##  Screenshots

![image](https://github.com/user-attachments/assets/bb2c3088-2364-4b7d-88c4-36f3119b03e4)
![image](https://github.com/user-attachments/assets/959d4923-bf0d-46fe-a604-89a0473fd564)
![WhatsApp Image 2025-06-08 at 22 41 02_d994ee32](https://github.com/user-attachments/assets/45d3af8a-bf5b-4061-915e-180af4ef53a7)
![WhatsApp Image 2025-06-08 at 22 42 16_30adeb53](https://github.com/user-attachments/assets/804cee86-0207-419e-a988-25e546d706f5)



---

##  Assignment Requirements Checklist

- [x] **API endpoint for date, time, and message**
- [x] **Database storage**
- [x] **Python web framework (Flask)**
- [x] **Multiple reminder methods (SMS, Email)**
- [x] **No delivery logic required (but implemented as bonus)**
- [x] **Professional UI/UX**
- [x] **Clear all reminders feature**
- [x] **IST timezone support**
- [x] **Error handling and validation**

---

##  Tools & Packages Used

- **Python 3.8+**
- **Flask**
- **Flask-SQLAlchemy**
- **Celery**
- **Redis**
- **Twilio**
- **pytz**
- **python-dotenv**
- **eventlet** (for Celery on Windows)
- **SMTP (Gmail)**
- **HTML5, CSS3, JavaScript**
- **Jinja2**
- **Font Awesome (icons)**

---

##  UI/UX Design Tools & Principles

- **Figma** (for wireframing and prototyping)
- **Custom CSS** (black primary color scheme)
- **Responsive design** (media queries, mobile-first)
- **Accessible navigation and controls**
- **Live feedback and animations**
  



