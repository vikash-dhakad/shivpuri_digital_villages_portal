# 🌾 Shivpuri Digital Village Portal (VillageConnect)

A full-stack Rural Governance & Digital Village platform built with **Python, Django REST Framework, MySQL, and Bootstrap 5** to digitize village services, grievance management, agricultural equipment sharing, and village finances.

---

## 🌟 Key Features

### 1. 👥 Multi-Role User Management
- **Three Distinct Roles**: `VILLAGER`, `FARMER`, and `PANCHAYAT_ADMIN` (Sarpanch).
- **Authentication**: JWT (JSON Web Tokens) with 60-min access token + 7-day rolling refresh token.
- **Forgot Password via OTP**: Powered by Fast2SMS integration with 6-digit cache-backed OTPs.
- **Role-Based Access Control (RBAC)** on all views and UI components.

### 2. 📢 Announcements & Notice Board
- Panchayat Admins can publish circulars, urgent announcements, and notices with file attachments.
- Villagers receive real-time notice updates relevant to their village.

### 3. 📝 Grievance & Complaint Redressal
- Gramvasis can lodge complaints with photo attachments and categorisation (Water, Road, Electricity, Sanitation, etc.).
- Real-time status tracking (`PENDING`, `IN_PROGRESS`, `RESOLVED`, `REJECTED`).
- Citizen Feedback & 5-Star Rating upon resolution.
- Automated escalation for grievances pending > 7 days.

### 4. 🚜 AgriTech & Farm Equipment Sharing
- Farmers can list, discover, and rent agricultural machinery (Tractors, Harvesters, Threshers).
- Real-time hourly cost calculation with live rent deduction and Panchayat revenue addition.
- Automated equipment release when rental duration expires.
- **Live Mandi Prices**: Real-time commodity price tracking via data.gov.in Agmarknet API with state/district filters.

### 5. 💰 Transparent Panchayat Finance & Projects
- Public budget allocation and expenditure tracking.
- Village development project monitoring with milestone progress bars.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Django 5.1, Django REST Framework (DRF), SimpleJWT
- **Database**: MySQL 8.4 (InnoDB, utf8mb4)
- **Frontend**: HTML5, CSS3, JavaScript (Fetch API), Bootstrap 5.3 (Dark Theme)
- **SMS Gateway**: Fast2SMS API

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- MySQL Server 8.0+

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vikash-dhakad/shivpuri_digital_villages_portal.git
   cd shivpuri_digital_villages_portal
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your MySQL credentials:
   ```env
   DB_NAME=villageconnect_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306
   ```

5. **Run Database Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create an Admin Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 📂 Project Architecture

```
villageconnect_django/
├── accounts/          # User auth, JWT, OTP service, Village models
├── agritech/          # Farm equipment rentals, Mandi prices, Agri tasks
├── announcements/     # Village news, notices & circulars
├── finance/           # Panchayat budgets & development projects
├── grievances/        # Complaints, photo attachments, ratings & escalations
├── notifications/     # In-app notifications & alert broadcasts
├── static/            # CSS, JavaScript (auth.js, main.js), icons
├── templates/         # Django Bootstrap 5 HTML templates
├── villageconnect/    # Django core configuration, settings, urls, celery
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 📄 License
This project is licensed under the MIT License.
