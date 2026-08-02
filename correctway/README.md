# CorrectWay — Django edition

A full Python/Django rewrite of the original CorrectWay MERN app (React +
Node/Express + MongoDB), grown into a complete official website. This
version is 100% Python on the backend and server-rendered Django
templates on the frontend — no Node.js, npm, or a separate API layer
required.

## What this app does

A 25-question yes/no career-fit quiz for students who've just finished
12th grade. Answers are scored (rule-based, fully explainable — no
external AI API calls) against 20 career profiles, and the top 3 matches
are shown, each paired with a suggested AI tool to explore that path
further.

## Full page list

| Page | URL | Notes |
|---|---|---|
| Home | `/` | Landing page |
| About | `/about/` | How the scoring works |
| Careers directory | `/careers-directory/` | Browse all 20 profiles without taking the quiz |
| FAQ | `/faq/` | Common questions |
| Contact | `/contact/` | Form, saved to the database, reviewable in `/admin/` |
| Register / Login / Logout | `/register/` `/login/` `/logout/` | Session-based auth |
| Profile | `/profile/` | Edit your name, see how many analyses you've taken |
| 25-Question Analysis | `/quiz/` | The quiz itself |
| Results | `/results/` | Your latest analysis |
| History | `/history/` | Logged-in users' past analyses |
| Privacy policy | `/privacy/` | Placeholder — review before production use |
| Terms of service | `/terms/` | Placeholder — review before production use |
| Admin | `/admin/` | Manage users, quiz results, and contact messages |
| 404 / 500 | — | Custom error pages (`templates/404.html`, `templates/500.html`) |

The nav is responsive: a hamburger menu appears on mobile, and the
footer links to every page above.

## Getting started

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit DJANGO_SECRET_KEY etc.

python manage.py migrate
python manage.py createsuperuser # optional, for /admin/
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## Project layout

```
correctway_django/
├── manage.py
├── requirements.txt
├── .env.example
├── correctway/            # Django project (settings, urls, wsgi/asgi)
├── careers/                # Django app: models, views, forms, career engine
│   ├── models.py            # Profile, QuizResult (replaces the Mongoose schemas)
│   ├── career_engine.py     # the scoring engine (replaces careerEngine.js)
│   ├── forms.py              # register/login form validation
│   ├── views.py               # replaces server.js + routes/auth.js + routes/quiz.js
│   └── migrations/
├── templates/                # replaces the React pages/components
│   ├── base.html               # replaces App.jsx + Navbar.jsx + main.jsx
│   ├── home.html, login.html, register.html, quiz.html, results.html, history.html
│   └── partials/logo.html      # replaces components/Logo.jsx
└── static/
    ├── css/style.css           # the non-Tailwind rules from index.css
    └── img/                      # the original logo/favicon SVGs
```

## How the original MERN pieces map onto Django

| Original (MERN)                              | Django equivalent |
|-----------------------------------------------|-------------------|
| `server/server.js`                            | `correctway/urls.py`, `correctway/wsgi.py` |
| `server/config/db.js` (MongoDB via Mongoose)   | `correctway/settings.py` `DATABASES` (SQLite via Django ORM by default — swap in Postgres/MySQL by editing this block) |
| `server/models/User.js`                       | Django's built-in `auth.User` + `careers.Profile` (adds the `role` field) |
| `server/models/QuizResult.js`                 | `careers.models.QuizResult` |
| `server/middleware/auth.js` (JWT bearer tokens)| `django.contrib.auth` session-based login (`@login_required`, `request.user`) |
| `server/routes/auth.js`                       | `careers/views.py`: `register_view`, `login_view`, `logout_view` |
| `server/routes/quiz.js`                       | `careers/views.py`: `quiz_submit`, `history_view` |
| `server/utils/careerEngine.js` + `client/src/data/careerEngine.js` (two copies) | `careers/career_engine.py` (one copy, used everywhere) |
| `client/src/App.jsx`, `main.jsx`               | `templates/base.html` |
| `client/src/components/Navbar.jsx`             | nav block in `templates/base.html` |
| `client/src/components/Logo.jsx`               | `templates/partials/logo.html` |
| `client/src/pages/Home.jsx`                    | `templates/home.html` |
| `client/src/pages/Login.jsx`, `Register.jsx`   | `templates/login.html`, `templates/register.html` + `careers/forms.py` |
| `client/src/pages/Quiz.jsx`                    | `templates/quiz.html` (same one-question-at-a-time UX, keyboard shortcuts, and progress bar, in vanilla JS) |
| `client/src/pages/Results.jsx`                 | `templates/results.html` |
| React Router (`react-router-dom`)              | Django's URL routing (`correctway/urls.py`) |
| `AuthContext` + `localStorage` token           | Django sessions (`request.user`, cookies) |
| Tailwind build via Vite                        | Tailwind via CDN script in `base.html`, configured with the same color/font tokens as the original `tailwind.config.js` |

## Notes

- The quiz page still feels like the original single-page quiz (one
  question at a time, `Y`/`N` keyboard shortcuts, progress bar) — that
  part is vanilla JavaScript embedded in `templates/quiz.html`, since
  that interactivity doesn't need a full framework. The heavy lifting
  (scoring, persistence, auth) is 100% server-side Python/Django.
- Swap SQLite for Postgres/MySQL any time by editing `DATABASES` in
  `correctway/settings.py` — no other code changes needed.
- Admin panel at `/admin/` lets you inspect `Profile` and `QuizResult`
  records directly.
