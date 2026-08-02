"""
Views for CorrectWay.

Rewritten from the original Express routes + React pages:

  GET  /                  <- client/src/pages/Home.jsx           -> home()
  GET/POST /register/     <- client/src/pages/Register.jsx +
                             POST /api/auth/register (routes/auth.js) -> register_view()
  GET/POST /login/        <- client/src/pages/Login.jsx +
                             POST /api/auth/login (routes/auth.js)    -> login_view()
  POST /logout/           <- AuthContext.logout()                     -> logout_view()
  GET  /quiz/             <- client/src/pages/Quiz.jsx                -> quiz_view()
  POST /quiz/submit/      <- POST /api/quiz/submit (routes/quiz.js)   -> quiz_submit()
  GET  /results/          <- client/src/pages/Results.jsx             -> results_view()
  GET  /history/          <- GET /api/quiz/history (routes/quiz.js)   -> history_view()

The original used JWT bearer tokens (server/middleware/auth.js) checked
on every API call. Since this is now a server-rendered Django app,
authentication is handled the standard Django way: signed session
cookies via django.contrib.auth, which is the direct equivalent of
"optionalAuth"/"requireAuth" but built into the framework.
"""
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render

from . import career_engine
from .forms import ContactForm, LoginForm, ProfileForm, RegisterForm
from .models import ContactMessage, Profile, QuizResult


def home(request):
    """Landing page — rewrite of client/src/pages/Home.jsx."""
    return render(request, "home.html")


def register_view(request):
    """
    Create an account and log the user in immediately, then send them
    to the quiz — mirrors Register.jsx calling api.register() then
    login(token, user) then navigate("/quiz").
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"].strip()
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.create_user(
                username=email, email=email, password=password, first_name=name
            )
            Profile.objects.create(user=user, role=Profile.STUDENT)

            user = authenticate(request, username=email, password=password)
            login(request, user)
            return redirect("quiz")
        return render(request, "register.html", {"form": form})

    return render(request, "register.html", {"form": RegisterForm()})


def login_view(request):
    """
    Authenticate by email + password — mirrors Login.jsx calling
    api.login() then login(token, user) then navigate("/quiz").
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        error = None
        if form.is_valid():
            email = form.cleaned_data["email"].lower().strip()
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("quiz")
            error = "Incorrect email or password."
        else:
            error = "Email and password are required."
        return render(request, "login.html", {"form": form, "error": error})

    return render(request, "login.html", {"form": LoginForm()})


def logout_view(request):
    """Mirrors AuthContext.logout() + navigate('/')."""
    logout(request)
    return redirect("home")


def quiz_view(request):
    """
    Render the 25-question analysis — mirrors Quiz.jsx. All questions
    are embedded as JSON and stepped through client-side with vanilla
    JS (progress bar, Y/N buttons, Y/N/Left-arrow keyboard shortcuts),
    the same UX the original React page had.
    """
    return render(
        request,
        "quiz.html",
        {"questions_json": json.dumps(career_engine.QUESTIONS)},
    )


def quiz_submit(request):
    """
    POST /quiz/submit/ — analyzes 25 yes/no answers and returns the top
    career matches. Saves to the database when the user is logged in.
    Direct rewrite of routes/quiz.js's POST /api/quiz/submit.
    """
    if request.method != "POST":
        return JsonResponse({"message": "POST required."}, status=405)

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON body."}, status=400)

    answers = body.get("answers")
    if not answers or not isinstance(answers, dict):
        return JsonResponse({"message": "answers object is required."}, status=400)

    # Normalize question-id keys to int, mirroring the original's
    # Mongoose Map<questionId, Boolean> flexibility with string/number keys.
    normalized_answers = {int(k): bool(v) for k, v in answers.items()}

    result = career_engine.analyze_answers(normalized_answers, top_n=3)

    saved_id = None
    if request.user.is_authenticated:
        saved = QuizResult.objects.create(
            user=request.user,
            answers=normalized_answers,
            top_matches=result["top"],
            category_scores=result["category_scores"],
            variety_preference=result["variety_preference"],
        )
        saved_id = saved.id

    # Stash the result in the session so the /results/ page (a plain
    # GET, matching the original's client-side route navigation) can
    # render it without needing a database round trip or query params.
    request.session["last_result"] = result

    return JsonResponse({**result, "saved_id": saved_id, "redirect": "/results/"})


def results_view(request):
    """
    Show the most recent analysis — mirrors Results.jsx reading
    useLocation().state.result. Here that ephemeral client-side
    "navigation state" becomes a session value instead.
    """
    result = request.session.get("last_result")
    return render(request, "results.html", {"result": result})


@login_required
def history_view(request):
    """GET /history/ — logged-in user's past results (routes/quiz.js's GET /api/quiz/history)."""
    results = QuizResult.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "history.html", {"results": results})


# ---------------------------------------------------------------------
# The pages below are new — they didn't exist in the original MERN app,
# and turn the quiz demo into a complete official website: an About
# page, a public directory of all 20 career profiles, an FAQ, a
# Contact form (stored in the database and visible in /admin/), and
# Privacy/Terms pages.
# ---------------------------------------------------------------------

def about_view(request):
    """GET /about/ — what CorrectWay is and how the scoring works."""
    return render(request, "about.html")


def careers_directory_view(request):
    """
    GET /careers-directory/ — browse all 20 career profiles and the AI
    tool paired with each one, without needing to take the quiz first.
    """
    return render(request, "careers_directory.html", {"careers": career_engine.CAREERS})


FAQS = [
    (
        "Is the career match generated by an AI model?",
        "No — the scoring is a transparent, rule-based system. Your yes/no "
        "answers add points to 12 strength categories, which are then "
        "compared against fixed weights for each of the 20 career "
        "profiles. It's deterministic and explainable, not a black box.",
    ),
    (
        "Do I need an account to take the quiz?",
        "No, you can take the 25-question analysis and see your top 3 "
        "matches without registering. Creating an account just lets you "
        "save each result and revisit your history later.",
    ),
    (
        "Can I retake the analysis?",
        "Yes, as many times as you like. Each submission is scored fresh "
        "from your current answers, and logged-in users can compare past "
        "attempts on the History page.",
    ),
    (
        "What do the suggested AI tools mean?",
        "Each of the 20 career profiles is paired with one AI tool "
        "relevant to exploring that field further — for example, Figma AI "
        "for UI/UX Design, or GitHub Copilot for Software Development. "
        "They're a suggested next step, not a requirement.",
    ),
    (
        "Is my data private?",
        "Your quiz answers and results are only visible to you and to "
        "site administrators. See the Privacy Policy for details.",
    ),
]


def faq_view(request):
    """GET /faq/ — frequently asked questions."""
    return render(request, "faq.html", {"faqs": FAQS})


def contact_view(request):
    """GET/POST /contact/ — public contact form, saved for admin review."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(**form.cleaned_data)
            messages.success(request, "Thanks — your message has been sent. We'll get back to you soon.")
            return redirect("contact")
        return render(request, "contact.html", {"form": form})
    return render(request, "contact.html", {"form": ContactForm()})


def privacy_view(request):
    """GET /privacy/ — privacy policy."""
    return render(request, "privacy.html")


def terms_view(request):
    """GET /terms/ — terms of service."""
    return render(request, "terms.html")


@login_required
def profile_view(request):
    """GET/POST /profile/ — view/update account name; links to history."""
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data["name"].strip()
            request.user.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("profile")
    else:
        form = ProfileForm(initial={"name": request.user.first_name})

    result_count = QuizResult.objects.filter(user=request.user).count()
    return render(request, "profile.html", {"form": form, "result_count": result_count})
