# MotoCare Pro — AI-Powered Bike Service Management System

A Django-based motorcycle service booking and tracking platform: customers book
a slot, choose a package or à-la-carte services, pick their engine oil, and
then follow the job through a live status timeline (Booked → ... → Delivered).
Separate dashboards exist for customers, mechanics, and admins.

Design direction: an **instrument-cluster / garage** aesthetic — asphalt-dark
surfaces, an ignition-orange accent, a `JetBrains Mono` numerals for data, and
a rev-gauge as the hero's signature visual — rather than a generic SaaS look.

## Tech stack

- Python 3.12+, Django 5
- SQLite for local dev, PostgreSQL for production (toggle via `USE_POSTGRES`)
- Bootstrap 5, Font Awesome, AOS (scroll animations), Chart.js (admin analytics)
- django-crispy-forms + crispy-bootstrap5 for form rendering
- Docker + docker-compose for containerized local/prod runs
- GitHub Actions CI (`.github/workflows/ci.yml`)

## Quick start (local, SQLite)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit values as needed

python manage.py migrate        # migrations are pre-generated — no makemigrations needed
python manage.py createsuperuser
python manage.py seed_demo_data # populates services, packages, oils, a mechanic login
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

- **Customer**: register from the site (you'll pick a security question + answer
  during signup — that's used for password resets, there's no email step).
  Add a bike, then book a service.
- **Mechanic demo login**: `mechanic_demo` / `MotoCare@123` — security question
  "What was the make of your first bike?" → answer `Bajaj` (created by `seed_demo_data`).
- **Admin**: the superuser you created; `/dashboard/` routes by role automatically,
  and `/admin/` is the full Django admin for managing catalogue data. Note a
  superuser created via `createsuperuser` has no security question set, so
  "forgot password" won't work for it — reset it via `/admin/` or the shell instead.

## Quick start (Docker + Postgres)

```bash
docker compose up --build
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_demo_data
```

## Project layout

```
MotoCarePro/
├── core/            # settings, root urls, wsgi/asgi
├── pages/           # landing, about, contact, FAQ + seed_demo_data command
├── accounts/        # custom User (role: customer/mechanic/admin), auth, security-question reset
├── bikes/           # customer garage (CRUD)
├── services/        # ServiceType, EngineOil, Modification, ServicePackage
├── mechanics/       # ServiceCenter, MechanicProfile
├── appointments/     # 6-step booking wizard, status tracking, coupons
├── reviews/         # customer feedback
├── dashboard/       # customer / mechanic / admin dashboards + role redirect
├── templates/       # all HTML, organized per app
├── static/css/style.css   # design system (CSS variables, components)
└── static/js/main.js      # navbar, theme toggle, gauge animation, AOS init
```

## What's implemented vs. stubbed

**Implemented:** role-based auth with a **security-question password reset**
(no email/OTP step — pick a question and answer at signup, answer it later to
set a new password), bike garage CRUD, the full 6-step booking flow
(date/slot/center → bike → services/package/mods → oil → pickup/drop →
payment/coupon), live status tracking with a progress timeline, mechanic job
list + status updates, admin analytics dashboard with Chart.js, reviews model,
demo data seeding, and **pre-generated migrations for every app** so `migrate`
works on a clean clone without running `makemigrations` first.

**Stubbed / left for integration:** Razorpay is wired as a "pay online now vs.
pay at center" choice but doesn't call the real Razorpay API — add your keys
to `.env` and integrate `razorpay-python` in `appointments/views.py::step6`.
Google Maps is embedded as a plain iframe; add `GOOGLE_MAPS_API_KEY` and swap
in the JS API for interactive maps. AWS S3 for media storage isn't configured
— add `django-storages` and point `STORAGES["default"]` at your bucket for
production. Beyond the core spec, things like blogs, wishlist, live chat, SMS
alerts, and QR-code receipts from the original brief are **not** built —
they'd each be a meaningful feature in their own right rather than a quick
add-on, so I've left them out rather than stub them badly. Say the word if
you want any of those built out next and I'll scope it properly.

## Suggested next step (per the original brief)

If you want to take this further into a production-grade portfolio piece:
Django REST Framework API layer + a separate React (Vite) frontend consuming
it over JWT, deployed to AWS (EC2 + S3 + Nginx + Gunicorn) with the included
GitHub Actions workflow extended into a full CI/CD pipeline, and Swagger/OpenAPI
docs via `drf-spectacular`. The current models and business logic translate
directly into DRF serializers/viewsets — the `Appointment` status machine and
the wizard's step data are the two pieces worth the most care in that port.

## Note on this environment

This project was hand-written in a sandbox without network access, so it
hasn't been run against a live Django install here — including the migration
files, which I wrote by hand to match the models exactly rather than
generating them with `makemigrations` (which needs Django installed). After
`pip install`, it's worth running:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

The second command should report "No changes detected" — if it doesn't, it
means a hand-written migration drifted from a model somewhere; run
`python manage.py makemigrations` to generate the missing piece and open an
issue/tell me so I can fix the source file.
