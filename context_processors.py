"""
Site-wide context processors.
"""

# (Google Translate code, native-script label, English label)
# English + the 5 languages requested explicitly come first; the rest
# fill the list out to 25 total, covering the languages most likely to
# be relevant to students across India, the Gulf, and beyond.
SITE_LANGUAGES = [
    ("en", "English", "English"),
    ("ta", "தமிழ்", "Tamil"),
    ("hi", "हिन्दी", "Hindi"),
    ("ml", "മലയാളം", "Malayalam"),
    ("te", "తెలుగు", "Telugu"),
    ("ar", "العربية", "Arabic"),
    ("bn", "বাংলা", "Bengali"),
    ("ur", "اردو", "Urdu"),
    ("pa", "ਪੰਜਾਬੀ", "Punjabi"),
    ("gu", "ગુજરાતી", "Gujarati"),
    ("mr", "मराठी", "Marathi"),
    ("kn", "ಕನ್ನಡ", "Kannada"),
    ("es", "Español", "Spanish"),
    ("fr", "Français", "French"),
    ("de", "Deutsch", "German"),
    ("pt", "Português", "Portuguese"),
    ("it", "Italiano", "Italian"),
    ("ru", "Русский", "Russian"),
    ("zh-CN", "中文", "Chinese"),
    ("ja", "日本語", "Japanese"),
    ("ko", "한국어", "Korean"),
    ("th", "ไทย", "Thai"),
    ("vi", "Tiếng Việt", "Vietnamese"),
    ("id", "Bahasa Indonesia", "Indonesian"),
    ("tr", "Türkçe", "Turkish"),
]


def site_languages(request):
    return {"languages": SITE_LANGUAGES}
