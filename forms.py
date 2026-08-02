"""
Forms for registration and login.

Mirrors the validation originally done in server/routes/auth.js:
  - name, email, and password are all required
  - password must be at least 6 characters
  - email must be unique (checked in the view against auth.User)
"""
from django import forms
from django.contrib.auth.models import User

# Shared Tailwind classes matching the original Field component in
# client/src/pages/Login.jsx, applied to every text/password input.
INPUT_CLASSES = (
    "focus-ring rounded border border-line bg-slate px-3 py-2.5 text-mist "
    "outline-none placeholder:text-mist/30 w-full"
)

# Same field, extra left padding to make room for a leading icon glyph
# (used on the login/register cards, which are drawn with icon-in-field styling).
ICON_INPUT_CLASSES = (
    "focus-ring rounded border border-line bg-slate pl-11 pr-3 py-2.5 text-mist "
    "outline-none placeholder:text-mist/30 w-full"
)

# Same again, with room on the right for a show/hide-password toggle button too.
PASSWORD_INPUT_CLASSES = (
    "focus-ring rounded border border-line bg-slate pl-11 pr-11 py-2.5 text-mist "
    "outline-none placeholder:text-mist/30 w-full"
)


class RegisterForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        required=True,
        label="Name",
        widget=forms.TextInput(attrs={"class": ICON_INPUT_CLASSES, "placeholder": "Your full name", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": ICON_INPUT_CLASSES, "placeholder": "you@example.com", "autocomplete": "email"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": PASSWORD_INPUT_CLASSES, "placeholder": "Min. 6 characters", "autocomplete": "new-password"}),
        min_length=6,
        required=True,
        label="Password (min. 6 characters)",
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": ICON_INPUT_CLASSES, "placeholder": "you@example.com", "autocomplete": "email"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": PASSWORD_INPUT_CLASSES, "placeholder": "Your password", "autocomplete": "current-password"}),
        required=True,
        label="Password",
    )


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        required=True,
        label="Name",
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES}),
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": INPUT_CLASSES}),
    )
    message = forms.CharField(
        required=True,
        label="Message",
        widget=forms.Textarea(attrs={"class": INPUT_CLASSES, "rows": 5}),
    )


class ProfileForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        required=True,
        label="Name",
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES}),
    )
