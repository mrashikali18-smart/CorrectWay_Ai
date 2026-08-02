"""
CorrectWay career-matching engine.

A transparent, rule-based "AI suggestion" scorer: 25 yes/no questions,
each tagged with the strength categories it signals, scored against
weighted career profiles. No external model call is required, so the
result is instant, explainable, and reproducible.

This is a direct Python port of the original JavaScript engine, which
existed in two copies in the Node/React project:
  - client/src/data/careerEngine.js  (client-side fallback scoring)
  - server/utils/careerEngine.js     (server-side source of truth)
Here there is only one copy, used everywhere by the Django views.
"""

CATEGORIES = [
    {"code": "analytical", "label": "Analytical Thinking"},
    {"code": "creative", "label": "Creativity"},
    {"code": "communication", "label": "Communication"},
    {"code": "handson", "label": "Hands-on / Technical Skill"},
    {"code": "empathy", "label": "Empathy & People Care"},
    {"code": "organization", "label": "Organization & Planning"},
    {"code": "technology", "label": "Technology & Systems"},
    {"code": "leadership", "label": "Leadership & Initiative"},
    {"code": "writing", "label": "Writing & Language"},
    {"code": "numbers", "label": "Numbers & Finance"},
    {"code": "science", "label": "Scientific Curiosity"},
    {"code": "design", "label": "Visual / Spatial Design"},
]

# 25 yes/no questions. Each maps to 1-2 categories.
QUESTIONS = [
    {"id": 1, "text": "I like breaking a problem down into pieces to find out why it happened.", "cats": ["analytical"]},
    {"id": 2, "text": "I enjoy coming up with new ideas and thinking outside the box.", "cats": ["creative"]},
    {"id": 3, "text": "Speaking in front of people and explaining my point clearly comes easily to me.", "cats": ["communication"]},
    {"id": 4, "text": "I like building or fixing things with my hands.", "cats": ["handson"]},
    {"id": 5, "text": "Listening to someone's problem and understanding how they feel comes naturally to me.", "cats": ["empathy"]},
    {"id": 6, "text": "I like planning my time and working off a to-do list.", "cats": ["organization"]},
    {"id": 7, "text": "When a new app or gadget comes out, I try it out right away.", "cats": ["technology"]},
    {"id": 8, "text": "Leading a group and making decisions feels like responsibility to me, not fear.", "cats": ["leadership"]},
    {"id": 9, "text": "I enjoy writing stories, essays, or social posts.", "cats": ["writing"]},
    {"id": 10, "text": "I'd rather have a job that's different every day than the same routine.", "cats": [], "routine_flag": True},
    {"id": 11, "text": "Thinking about numbers, budgets, or accounts is genuinely interesting to me.", "cats": ["numbers"]},
    {"id": 12, "text": "I like investigating why and how natural things happen.", "cats": ["science"]},
    {"id": 13, "text": "I have a good sense for colors, layout, or visual design.", "cats": ["design"]},
    {"id": 14, "text": "I like analyzing data or statistics to reach a conclusion.", "cats": ["analytical", "numbers"]},
    {"id": 15, "text": "I like redesigning or reimagining how something looks or works.", "cats": ["creative", "design"]},
    {"id": 16, "text": "I can explain a difficult topic in a way that's easy for others to understand.", "cats": ["communication", "writing"]},
    {"id": 17, "text": "I enjoy working with machines, circuits, or tools.", "cats": ["handson", "technology"]},
    {"id": 18, "text": "I get real satisfaction from helping others, even as a full-time job.", "cats": ["empathy"]},
    {"id": 19, "text": "I'm good at completing a project step by step, on a timeline.", "cats": ["organization", "leadership"]},
    {"id": 20, "text": "I'm curious about coding, apps, or building websites.", "cats": ["technology", "analytical"]},
    {"id": 21, "text": "I'd take the initiative to organize a new group or activity myself.", "cats": ["leadership", "communication"]},
    {"id": 22, "text": "I'm interested in writing poetry, lyrics, or scripts.", "cats": ["writing", "creative"]},
    {"id": 23, "text": "I enjoy thinking about saving and investing money.", "cats": ["numbers", "analytical"]},
    {"id": 24, "text": "I enjoy running experiments and recording results, like in a lab.", "cats": ["science", "organization"]},
    {"id": 25, "text": "I'm drawn to visual arts like drawing, photography, or video editing.", "cats": ["design", "creative"]},
]

# 20 career profiles. `w` = weight (0-2) per category code.
CAREERS = [
    {"title": "Data Scientist", "tool": "ChatGPT / Kaggle", "w": {"analytical": 2, "numbers": 2, "technology": 1, "science": 1}},
    {"title": "Software Developer", "tool": "GitHub Copilot", "w": {"technology": 2, "analytical": 1, "handson": 1}},
    {"title": "UI/UX Designer", "tool": "Figma AI", "w": {"design": 2, "creative": 2, "empathy": 1}},
    {"title": "Digital Marketer", "tool": "ChatGPT + Canva", "w": {"communication": 2, "creative": 1, "writing": 1}},
    {"title": "Chartered Accountant / Finance Analyst", "tool": "Excel Copilot", "w": {"numbers": 2, "organization": 2, "analytical": 1}},
    {"title": "Mechanical / Automotive Engineer", "tool": "Autodesk Fusion AI", "w": {"handson": 2, "science": 1, "analytical": 1}},
    {"title": "Content Writer / Journalist", "tool": "ChatGPT / Grammarly", "w": {"writing": 2, "communication": 1, "creative": 1}},
    {"title": "Psychologist / Counselor", "tool": "Woebot (study aid)", "w": {"empathy": 2, "communication": 2}},
    {"title": "Entrepreneur / Startup Founder", "tool": "ChatGPT + Notion AI", "w": {"leadership": 2, "creative": 1, "organization": 1}},
    {"title": "Civil / Structural Engineer", "tool": "AutoCAD AI tools", "w": {"handson": 1, "science": 1, "analytical": 1, "organization": 1}},
    {"title": "Doctor / Medical Professional", "tool": "PubMed + AI research tools", "w": {"science": 2, "empathy": 2, "organization": 1}},
    {"title": "Teacher / Trainer", "tool": "ChatGPT lesson planner", "w": {"communication": 2, "empathy": 1, "organization": 1}},
    {"title": "Graphic / Motion Designer", "tool": "Adobe Firefly", "w": {"design": 2, "creative": 2}},
    {"title": "Cybersecurity Analyst", "tool": "ChatGPT + Shodan", "w": {"technology": 2, "analytical": 2}},
    {"title": "Project Manager", "tool": "Notion AI / Asana", "w": {"organization": 2, "leadership": 2, "communication": 1}},
    {"title": "Research Scientist", "tool": "Elicit / Consensus AI", "w": {"science": 2, "analytical": 2}},
    {"title": "Investment Banker / Financial Analyst", "tool": "ChatGPT + Bloomberg", "w": {"numbers": 2, "analytical": 1, "leadership": 1}},
    {"title": "Video Editor / Filmmaker", "tool": "Runway ML", "w": {"design": 1, "creative": 2, "technology": 1}},
    {"title": "HR / People Operations", "tool": "ChatGPT interview prep", "w": {"empathy": 2, "communication": 1, "organization": 1}},
    {"title": "Architect", "tool": "Midjourney + AutoCAD", "w": {"design": 2, "science": 1, "handson": 1}},
]


def analyze_answers(answers, top_n=3):
    """
    Score all 25 answers against every career profile and return the
    ranked top matches — the "AI suggestion" step: deterministic,
    explainable scoring rather than a black-box call, so results are
    instant and reproducible.

    :param answers: dict mapping questionId (int or str) -> bool
    :param top_n: how many top matches to return
    :return: dict with keys "top", "category_scores", "variety_preference"
    """
    cat_score = {c["code"]: 0 for c in CATEGORIES}

    routine_yes = 0
    routine_total = 0

    for q in QUESTIONS:
        answer = bool(answers.get(q["id"]) or answers.get(str(q["id"])))
        if q.get("routine_flag"):
            routine_total += 1
            if answer:
                routine_yes += 1
            continue
        if not answer:
            continue
        for cat in q["cats"]:
            cat_score[cat] += 1

    ranked = []
    for career in CAREERS:
        raw = 0
        max_score = 0
        for cat, weight in career["w"].items():
            max_score += weight * 3  # rough ceiling per category for normalization
            raw += weight * cat_score.get(cat, 0)
        pct = min(100, round((raw / max_score) * 100)) if max_score > 0 else 0
        ranked.append({"title": career["title"], "tool": career["tool"], "pct": pct})

    ranked.sort(key=lambda c: c["pct"], reverse=True)

    variety = routine_total > 0 and (routine_yes / routine_total) >= 0.5

    return {
        "top": ranked[:top_n],
        "category_scores": cat_score,
        "variety_preference": variety,
    }
