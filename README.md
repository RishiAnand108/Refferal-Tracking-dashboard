# Concave Insights — Referral Tracking Dashboard

A focused Django application to track and attribute referrals
from a consumer panel. It records who referred whom, manages
respondent lifecycle stages (Lead → Fit → Completion), and
provides an admin dashboard for monitoring and payouts.

Key goals:
- Prevent missed referral attribution at signup
- Keep referral attribution simple and auditable
- Provide admin tools for search, filtering and status updates

## Features
- Short referral links with session-based attribution
- Self-referential `Respondent` model to build referral trees
- Respondent lifecycle tracking: `lead`, `fit`, `completion`
- Admin UI with search, filters and list display for models
- Management command to load baseline respondents (`load_baseline_data`)

## Tech Stack
- Python 3.11+ and Django 5.x
- SQLite (default dev) — easily switchable to PostgreSQL in production
- Bootstrap 5 for the admin-facing templates
- Django REST Framework (if building APIs)

## Quickstart (Development)
1. Clone the repo and change into the project folder:

```bash
git clone https://github.com/YOUR_USERNAME/concave-referral-tracker.git
cd concave-referral-tracker
```

2. Create & activate a virtual environment:

```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# macOS / Linux
source venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations and load baseline data (optional):

```bash
python manage.py migrate
python manage.py load_baseline_data
```

5. Create a superuser and run the server:

```bash
python manage.py createsuperuser
python manage.py runserver
```

Open http://localhost:8000 for the dashboard and
http://localhost:8000/admin for the Django admin.

## Important Management Commands
- `python manage.py load_baseline_data` — loads `data/baseline_respondents.csv`
- `python manage.py migrate` — apply DB migrations
- `python manage.py createsuperuser` — create admin account

## Configuration / Environment
Recommended environment variables (use a `.env` file or your host):

- `SECRET_KEY` — Django secret key
- `DEBUG` — `True` for development
- `DATABASE_URL` — e.g. `sqlite:///db.sqlite3` or a PostgreSQL URL

In `config/settings.py` you can switch DB engines and other settings.

## Data Model Summary
- Respondent: stores respondent contact info, `referral_code`,
  `referred_by` (self-FK), `status`, and cooling period fields.
- ReferralStatus (or equivalent): records referral events,
  stages (`lead`, `fit`, `completion`) and payout status.

For full field definitions see `panel/models.py` and `users/models.py`.

## Tests
Run Django tests with:

```bash
python manage.py test
```

## Deployment Notes
- Use PostgreSQL for production and set `DEBUG=False`.
- Collect static files if serving static assets: `python manage.py collectstatic`.
- Configure a WSGI/ASGI server (Gunicorn / Daphne) and a reverse proxy (Nginx).

## Contributing
- Please open issues or PRs for bug fixes or feature requests.
- Keep changes small and focused; include tests for model/query logic.

## License & Contact
This project is provided as-is. Add your preferred license here.

For questions or help, contact the project owner or open an issue.

---
Updated README generated to reflect repository structure and usage.
