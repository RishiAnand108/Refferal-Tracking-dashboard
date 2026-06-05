# Concave Insights — Referral Tracking System

A full-stack Django web application that automates the 
referral lifecycle for Concave Insights' consumer panel network.

## Problem Solved
Eliminates the manual attribution bottleneck where referred 
respondents forget to mention who referred them. The system 
automatically tracks referral links, attributes sign-ups to 
the correct referrer, and exposes status progress transparently.

## Tech Stack
- Backend: Django 5.x
- Database: SQLite (dev) / PostgreSQL (prod)
- Frontend: Bootstrap 5
- API: Django REST Framework
- Auth: Django built-in auth

## Referral Flow

Referrer shares unique link
↓
New person clicks /refer/<code>/
↓
System stores referrer in session
↓
New person signs up
↓
Attribution automatic — no manual entry needed
↓
Status tracked: Lead → Fit → Completion
↓
Bonus paid on Completion

## Setup — Run in under 5 minutes

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/concave-referral-tracker.git
cd concave-referral-tracker
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Load baseline data
```bash
python manage.py load_baseline_data
```

### 6. Create admin user
```bash
python manage.py createsuperuser
```

### 7. Run server
```bash
python manage.py runserver
```

### 8. Open in browser
http://localhost:8000          → Dashboard
http://localhost:8000/admin    → Django Admin

## Database Schema

### Respondent
| Field | Type | Description |
|-------|------|-------------|
| unique_id | CharField | Auto-generated CI-2026-XXXX |
| name | CharField | Full name |
| email | EmailField | Unique |
| phone | CharField | 10 digits |
| city | CharField | Mumbai/Delhi/Bangalore etc |
| category | CharField | Healthcare/Finance/Retail etc |
| status | CharField | active/cooloff/inactive |
| referred_by | ForeignKey | Self-referential FK |
| referral_code | UUIDField | Unique per respondent |
| cool_off_until | DateField | 3 months after last survey |

### ReferralStatus
| Field | Type | Description |
|-------|------|-------------|
| referrer | ForeignKey | Who shared the link |
| referred | ForeignKey | Who signed up |
| stage | CharField | lead / fit / completion |
| bonus_amount | DecimalField | Payout amount |
| is_paid | BooleanField | Payment status |

## Architecture Decisions
- Self-referential ForeignKey on Respondent for referral tree
- UUID referral codes — unguessable, unique per person
- Session-based referral attribution — works even if user 
  closes browser and returns later
- 3-month cooloff enforced at signup validation level
- Q objects for multi-field search without raw SQL

## Environment Variables

SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
