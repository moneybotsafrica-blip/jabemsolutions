# Jabem Solutions Ltd — Django Website

A Django site for an IT company selling and supporting POS (point-of-sale)
hardware and software: public marketing pages + product catalog, full
inventory management via Django admin, and a client portal for support
tickets and service requests.

## Apps

- **core** — marketing pages: home, about, services, contact (with an email-sending contact form).
- **catalog** — `Category`, `Brand`, `Product`, `Stock`, `StockMovement`. Public product listing/detail
  with filtering by type/category and search. Inventory is tracked with an atomic
  `Stock.adjust()` method (row-locked with `select_for_update`) that records every
  change as a `StockMovement` and blocks overselling.
- **accounts** — custom `User` model (`is_client` flag) + `ClientProfile` (company info).
  Public client sign-up form.
- **portal** — login-required client area: dashboard, `SupportTicket` (with threaded
  `TicketComment` replies), and `ServiceRequest` (installation/maintenance/training/
  consultation, with preferred date and location). Staff users (`is_staff=True`) see
  all clients' tickets/requests; regular clients only see their own.

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit:
- `/` — marketing site
- `/products/` — product catalog
- `/accounts/signup/` — client sign-up
- `/portal/` — client portal (requires login)
- `/admin/` — inventory & ticket/request management (requires staff account)

## Managing inventory

Products, categories, brands, and stock levels are managed through **Django admin**
(`/admin/`). Each product's stock badge is color-coded (red = at/below its reorder
level). Stock changes should go through `Stock.adjust(delta, movement_type, reference,
created_by)` rather than editing `quantity_on_hand` directly, so every change is
captured in the `StockMovement` audit trail. `StockMovement` records are read-only
in the admin to preserve that history.

## Turning a user into staff (internal team member)

In `/admin/`, edit the user and check **Staff status**. Staff accounts can see and
manage every client's tickets and service requests, and get an "Admin" link in the
site nav.

## Configuration

Key settings are read from environment variables (with sensible dev defaults) in
`config/settings.py`:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`True`/`False`)
- `DJANGO_ALLOWED_HOSTS` (comma-separated)

Email currently uses Django's console backend (prints to the terminal) — swap
`EMAIL_BACKEND` in `settings.py` for a real SMTP backend (e.g. Gmail, SendGrid,
Africa's Talking SMTP) before going live.

## Client-facing extras

- `/portal/profile/` — clients can update their name, email, phone, company,
  and industry after signing up.
- Custom `404`, `403`, and `500` error pages (branded, matching the site).
- Django admin is rebranded with the site name instead of the "Django
  administration" default.

## Running the test suite

```bash
python manage.py test
```

17 tests cover: inventory adjustments (stock in/out, oversell blocking, low-stock
flagging), public page rendering, product visibility rules, portal access control
(an owner can view their own ticket, a different client gets `403`, staff can view
any ticket), and the sign-up → profile-creation → auto-login flow.

## Deploying

The project ships ready for a typical PaaS (Render, Railway, Heroku-style) deploy:

- **`Procfile`** — runs `gunicorn config.wsgi` for the web process and
  `python manage.py migrate` on release.
- **`whitenoise`** — serves compressed, cache-busted static files directly from
  the app in production, no separate static host needed for a first deploy.
- **`dj-database-url` + `psycopg2-binary`** — set a `DATABASE_URL` env var
  (e.g. `postgres://user:pass@host:5432/dbname`) to use Postgres; leave it unset
  to keep using SQLite.
- **`.env.example`** — copy to `.env` and fill in real values before deploying.

```bash
cp .env.example .env    # then edit .env with real values
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi
```

## Before deploying to production

- Set `DJANGO_DEBUG=False` and a real, long random `DJANGO_SECRET_KEY`
  (the app auto-enables HTTPS redirects, secure cookies, and HSTS once
  `DEBUG=False` — see `config/settings.py`).
- Set `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` to your real domain(s).
- Point `DATABASE_URL` at PostgreSQL for concurrent write safety (important given
  the row-locking in `Stock.adjust()`).
- Configure a real `EMAIL_BACKEND` for the contact form and staff notifications
  (currently the console backend, which just prints emails to the server log).
- Run `python manage.py check --deploy` before going live — it should return
  no issues once `DEBUG=False` and the env vars above are set.
