# 🤖 AI Interview Question Generator

A full-stack web application built with **Django** and **Google Gemini AI** that helps users prepare for job interviews by generating customised interview questions with answers and explanations.

---

## ✨ Features

- **AI-Powered Question Generation** — Generate Q&A or MCQ questions for any job role and difficulty level using Google Gemini
- **Email Verification** — OTP-based email verification on registration via Gmail SMTP
- **Forgot Password** — Secure password reset flow with OTP sent to Gmail
- **Session History** — Browse, revisit, and delete past interview sessions
- **PDF Download** — Download any session as a formatted PDF with questions and answers
- **Show / Hide Answers** — Toggle answers and explanations on the generate and session detail pages
- **Profile Management** — View stats, change profile picture, and update password
- **Responsive UI** — Clean, modern interface with Inter font and gradient design system

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9, Django 4.2 |
| AI | Google Gemini 2.5 Flash (`google-generativeai`) |
| Database | MySQL |
| PDF Generation | ReportLab |
| Email | Gmail SMTP |
| Frontend | HTML, CSS (custom), Font Awesome 6, JavaScript |
| Auth | Django built-in auth + custom OTP flow |

---

## 📸 Screenshots

> _Add screenshots here after deployment_

| Login | Dashboard | Generate |
|---|---|---|
| ![Login]() | ![Dashboard]() | ![Generate]() |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- MySQL
- A Google account with 2-Step Verification enabled (for Gmail SMTP)
- A Google Gemini API key

---

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-interview-question-generator.git
cd ai-interview-question-generator
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the MySQL database

```sql
CREATE DATABASE interview_ai;
```

### 5. Set up environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_app_password
```

> **Gmail App Password:** Go to Google Account → Security → 2-Step Verification → App Passwords → Generate one for "Mail".

### 6. Update `settings.py`

Open `AI_InterviewQuestion_Generator/settings.py` and update the database credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'interview_ai',
        'USER': 'root',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 7. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Start the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** in your browser.

---

## 📁 Project Structure

```
AI_InterviewQuestion_Generator/
│
├── AI_InterviewQuestion_Generator/   # Project settings & root URLs
│   ├── settings.py
│   └── urls.py
│
├── accounts/                         # Auth app
│   ├── models.py                     # Profile model
│   ├── views.py                      # Register, login, OTP, forgot password
│   ├── forms.py
│   └── urls.py
│
├── generator/                        # Core app
│   ├── models.py                     # InterviewSession model
│   ├── views.py                      # Generate, history, session detail, PDF
│   ├── gemini_service.py             # Gemini API integration
│   └── urls.py
│
├── template/                         # All HTML templates
├── static/
│   └── css/                          # All CSS files
├── media/                            # Uploaded profile pictures
├── .env                              # Environment variables (not committed)
├── requirements.txt
└── manage.py
```

---

## 📦 Requirements

Generate with:

```bash
pip freeze > requirements.txt
```

Key packages:

```
Django==4.2.20
google-generativeai
python-dotenv
mysqlclient
reportlab
Pillow
```

---

## 🔒 Security Notes

- Never commit `.env` or `settings.py` with real credentials to GitHub
- Use Django's `SECRET_KEY` from environment variables in production
- Set `DEBUG=False` before deploying to production

---

## 🙋‍♀️ Author

**Vishakha**
- GitHub: [@your-username](https://github.com/your-username)

---

## 📄 License

This project is for educational purposes.
