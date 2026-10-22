import os
import random
import re
import sqlite3
import time
from flask import Flask, request, render_template_string, session, redirect, url_for, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    # Local development fallback only. Set SECRET_KEY in your hosting dashboard.
    app.secret_key = "local-dev-only-change-before-deployment"

DATABASE = os.environ.get("DATABASE_PATH", "mindrush.sqlite3")
ROUND_SIZE = 5
MIN_NICK = 2
MAX_NICK = 16

QUESTIONS = [
    {"id":"logic1","category":"LOGIC","question":"A number doubled and then increased by 6 equals 20. What is the number?","options":["5","7","8","13"],"answer":"7","explanation":"2x + 6 = 20, so 2x = 14 and x = 7."},
    {"id":"science1","category":"SCIENCE","question":"Which planet is best known for its prominent rings?","options":["Mars","Venus","Saturn","Mercury"],"answer":"Saturn","explanation":"Saturn's large, bright ring system is made mostly of ice and rocky particles."},
    {"id":"maths1","category":"MATHS","question":"What is 15% of 200?","options":["15","20","30","35"],"answer":"30","explanation":"10% of 200 is 20 and 5% is 10, so 15% is 30."},
    {"id":"coding1","category":"CODING","question":"In Python, which keyword starts a conditional branch?","options":["loop","if","def","print"],"answer":"if","explanation":"Python uses if to test a condition, with elif and else for other branches."},
    {"id":"logic2","category":"LOGIC","question":"What comes next: 2, 6, 12, 20, 30, ...?","options":["36","40","42","44"],"answer":"42","explanation":"The gaps are +4, +6, +8, +10, so the next gap is +12. 30 + 12 = 42."},
    {"id":"science2","category":"SCIENCE","question":"What is the chemical symbol for oxygen?","options":["Ox","O","Og","Oy"],"answer":"O","explanation":"The chemical symbol for oxygen is O."},
    {"id":"maths2","category":"MATHS","question":"What is 9 × 7?","options":["56","63","72","79"],"answer":"63","explanation":"9 × 7 = 63."},
    {"id":"science3","category":"SCIENCE","question":"Which force pulls objects toward Earth?","options":["Magnetism","Friction","Gravity","Electricity"],"answer":"Gravity","explanation":"Gravity attracts objects with mass toward one another."},
    {"id":"coding2","category":"CODING","question":"What does print(3 + 2) display in Python?","options":["32","5","3 + 2","Error"],"answer":"5","explanation":"Python evaluates 3 + 2 first, then print displays 5."},
    {"id":"logic3","category":"LOGIC","question":"If all Zorbs are blue and Kai is a Zorb, what must be true?","options":["Kai is blue","Kai is tall","All blue things are Zorbs","Kai is not blue"],"answer":"Kai is blue","explanation":"If every Zorb is blue and Kai is a Zorb, Kai must be blue."},
]

def connect_db():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL,
                score INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                duration_seconds INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS scores_rank_idx ON scores(score DESC, duration_seconds ASC, created_at ASC)")

init_db()

CSS = r"""
:root{color-scheme:dark;--bg:#0b1024;--panel:#151d3c;--cyan:#66f2e3;--pink:#ff76c8;--muted:#aab5d8}
*{box-sizing:border-box}body{margin:0;min-height:100vh;font-family:system-ui,Segoe UI,sans-serif;color:#f6f7ff;background:radial-gradient(circle at 15% 15%,#29215d 0,transparent 32%),radial-gradient(circle at 90% 85%,#173e58 0,transparent 30%),var(--bg);padding:22px}
main{width:min(780px,100%);margin:0 auto}.top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:18px;flex-wrap:wrap}
.brand{letter-spacing:.16em;font-size:.8rem;color:var(--cyan);font-weight:900}.pill{border:1px solid #344064;border-radius:999px;padding:8px 12px;color:var(--muted);font-size:.85rem}
.card{background:linear-gradient(145deg,rgba(26,35,72,.97),rgba(15,23,48,.97));border:1px solid #303b67;border-radius:24px;padding:clamp(20px,5vw,42px);box-shadow:0 24px 80px #0005}
h1{font-size:clamp(2.3rem,8vw,4.4rem);line-height:.96;margin:12px 0 18px;letter-spacing:-.06em}h1 span{color:var(--cyan)}h2{font-size:clamp(1.3rem,4vw,2rem);line-height:1.25;margin:10px 0 18px}
p{color:var(--muted);line-height:1.65}.eyebrow{color:var(--pink);font-size:.78rem;letter-spacing:.18em;font-weight:850}
button,.btn{cursor:pointer;display:inline-block;border:0;border-radius:12px;padding:14px 18px;font-size:1rem;font-weight:850;color:#071323;background:var(--cyan);text-decoration:none}
button:hover,.btn:hover{filter:brightness(1.06)}input[type=text]{width:100%;background:#0d1530;color:white;border:1px solid #3b4772;border-radius:12px;padding:15px;font-size:1rem;margin:8px 0 16px}
.options{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:22px 0}.option{display:flex;gap:12px;align-items:center;text-align:left;background:#111a37;color:#f6f7ff;border:1px solid #3b4772;padding:15px;border-radius:14px;font-weight:650}.option input{accent-color:var(--cyan);width:18px;height:18px}
.option:has(input:checked){border-color:var(--cyan);background:#183349}.stats{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0}.stat{background:#0d1530;border:1px solid #303b67;border-radius:14px;padding:12px 16px;flex:1;min-width:100px}.stat b{display:block;font-size:1.35rem;color:var(--cyan)}.small{font-size:.85rem}.progress{height:7px;border-radius:9px;background:#303957;overflow:hidden;margin:16px 0 24px}.progress span{display:block;height:100%;background:linear-gradient(90deg,var(--cyan),var(--pink))}
.feedback{margin:18px 0;padding:16px;border-radius:14px;background:#0d1530;border:1px solid #344064}.feedback strong{color:var(--cyan)}table{width:100%;border-collapse:collapse;margin-top:14px}th,td{text-align:left;padding:12px 8px;border-bottom:1px solid #303b67}th{color:var(--muted);font-size:.85rem}.rank{color:var(--cyan);font-weight:900}.footer{text-align:center;font-size:.8rem;color:#7f8bb4;margin:18px 0 0}.alert{background:#432338;border:1px solid #814366;padding:12px;border-radius:12px;color:#ffe1f2;margin:12px 0}
@media(max-width:520px){.options{grid-template-columns:1fr}body{padding:14px}th,td{padding:10px 4px;font-size:.9rem}}
"""

PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0b1024"><title>Project MindRush</title><style>""" + CSS + r"""</style></head><body><main>
<div class="top"><div class="brand">✦ MINDRUSH / COMPETITION BETA</div><a class="pill" href="{{ url_for('leaderboard') }}">🏆 Leaderboard</a></div>
<section class="card">
{% if screen == "start" %}
<div class="eyebrow">YOUR BRAIN. YOUR MISSION.</div><h1>PROJECT<br><span>MINDRUSH</span></h1>
<p>A mystery challenge across logic, maths, science and coding. Solve five questions, earn XP, and see how you rank.</p>
<div class="stats"><div class="stat"><b>5</b><span class="small">questions per run</span></div><div class="stat"><b>100 XP</b><span class="small">per correct answer</span></div><div class="stat"><b>🏆</b><span class="small">shared leaderboard</span></div></div>
{% if error %}<div class="alert">{{ error }}</div>{% endif %}
<form method="post" action="{{ url_for('start_game') }}"><label for="nickname"><strong>Choose a nickname</strong></label><input id="nickname" name="nickname" type="text" minlength="2" maxlength="16" pattern="[A-Za-z0-9_-]{2,16}" required autocomplete="nickname" placeholder="e.g. BrainRocket"><p class="small">Use 2–16 letters, numbers, underscores or hyphens. Don't use your real name or contact details.</p><button type="submit">START MISSION →</button></form>
{% elif screen == "question" %}
<div class="eyebrow">{{ question.category }} CHALLENGE</div><div class="progress"><span style="width:{{ (index / total * 100)|int }}%"></span></div>
<div class="top"><div class="pill">MISSION {{ index }} / {{ total }}</div><div class="pill">⚡ {{ score }} XP</div></div><h2>{{ question.question }}</h2>
{% if error %}<div class="alert">{{ error }}</div>{% endif %}
<form method="post" action="{{ url_for('answer_question') }}"><input type="hidden" name="csrf" value="{{ csrf }}"><label><strong>Select one answer</strong></label><div class="options">{% for option in question.options %}<label class="option"><input type="radio" name="answer" value="{{ option }}" required><span>{{ option }}</span></label>{% endfor %}</div><button type="submit">LOCK IN ANSWER →</button></form>
{% elif screen == "feedback" %}
<div class="eyebrow">MISSION {{ index }} DEBRIEF</div><h2>{% if correct %}⚡ NICE WORK, BRAINHACKER!{% else %}🧩 EVERY MISS IS A CLUE.{% endif %}</h2>
<div class="feedback"><strong>{% if correct %}+100 XP{% else %}Correct answer: {{ question.answer }}{% endif %}</strong><p>{{ question.explanation }}</p></div>
<div class="stats"><div class="stat"><b>{{ score }}</b><span class="small">total XP</span></div><div class="stat"><b>{{ index }}/{{ total }}</b><span class="small">challenges done</span></div></div>
<form method="post" action="{{ url_for('next_question') }}"><input type="hidden" name="csrf" value="{{ csrf }}"><button type="submit">{% if index < total %}NEXT CHALLENGE →{% else %}SUBMIT SCORE →{% endif %}</button></form>
{% elif screen == "result" %}
<div class="eyebrow">MISSION COMPLETE</div><h1>{% if score >= 400 %}BRAIN<br><span>LEGEND.</span>{% elif score >= 200 %}SKILL<br><span>UNLOCKED.</span>{% else %}FIRST<br><span>LEVEL UP.</span>{% endif %}</h1>
<p>Your score has been recorded on the leaderboard. Final rank can change as other players complete the competition.</p>
<div class="stats"><div class="stat"><b>{{ score }}</b><span class="small">XP earned</span></div><div class="stat"><b>{{ correct_count }}/{{ total }}</b><span class="small">correct answers</span></div></div>
<a class="btn" href="{{ url_for('leaderboard') }}">VIEW LEADERBOARD →</a>
<p><strong>Ready to power up your learning?</strong><br>Explore learning resources and courses.</p><a class="btn" href="https://unacademy.com/" target="_blank" rel="noopener noreferrer">EXPLORE UNACADEMY ↗</a>
<p class="small">Independent promotional prototype; not an official Unacademy game. See competition rules from the organiser.</p>
<a class="pill" href="{{ url_for('index') }}">Back to home</a>
{% elif screen == "leaderboard" %}
<div class="eyebrow">WHO'S LEADING?</div><h1>TOP <span>BRAIN</span><br>HACKERS</h1><p>Rankings are ordered by score, then faster completion time. If scores and times match, the earlier submission ranks first.</p>
{% if scores %}<table><thead><tr><th>Rank</th><th>Nickname</th><th>Score</th><th>Time</th></tr></thead><tbody>{% for row in scores %}<tr><td class="rank">#{{ loop.index }}</td><td>{{ row["nickname"] }}</td><td>{{ row["score"] }} XP</td><td>{{ row["duration_seconds"] }}s</td></tr>{% endfor %}</tbody></table>{% else %}<p>No scores yet. Be the first to play!</p>{% endif %}
<p class="small">Only nicknames are shown. Do not enter your real name or personal information. Scores may be reviewed by the organiser before prizes are awarded.</p><a class="btn" href="{{ url_for('index') }}">PLAY MINDRUSH →</a>
{% endif %}
</section><div class="footer">PROJECT MINDRUSH · Browser game · No account needed</div></main></body></html>"""

def render(screen, **kwargs):
    return render_template_string(PAGE, screen=screen, **kwargs)

def csrf_token():
    if "csrf" not in session:
        session["csrf"] = os.urandom(24).hex()
    return session["csrf"]

def valid_csrf():
    return session.get("csrf") and request.form.get("csrf") == session.get("csrf")

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/")
def index():
    return render("start", error=None)

@app.post("/start")
def start_game():
    nickname = request.form.get("nickname", "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{2,16}", nickname):
        return render("start", error="Please use 2–16 letters, numbers, underscores or hyphens.")
    chosen = random.sample(QUESTIONS, ROUND_SIZE)
    session["nickname"] = nickname
    session["round"] = [q["id"] for q in chosen]
    session["position"] = 0
    session["score"] = 0
    session["correct_count"] = 0
    session["started_at"] = time.time()
    session["answered"] = []
    session.pop("score_saved", None)
    session["csrf"] = os.urandom(24).hex()
    return redirect(url_for("play"))

@app.get("/play")
def play():
    ids = session.get("round")
    pos = session.get("position")
    if not ids or pos is None:
        return redirect(url_for("index"))
    if pos >= len(ids):
        return redirect(url_for("finish"))
    question = next(q for q in QUESTIONS if q["id"] == ids[pos])
    return render("question", question=question, index=pos+1, total=len(ids),
                  score=session.get("score", 0), csrf=csrf_token(), error=None)

@app.post("/answer")
def answer_question():
    if not valid_csrf():
        abort(400, "Invalid form token. Please refresh and try again.")
    ids = session.get("round")
    pos = session.get("position")
    if not ids or pos is None or pos >= len(ids):
        return redirect(url_for("index"))
    answered = session.get("answered", [])
    if pos in answered:
        return redirect(url_for("play"))
    question = next(q for q in QUESTIONS if q["id"] == ids[pos])
    chosen = request.form.get("answer", "")
    if chosen not in question["options"]:
        return render("question", question=question, index=pos+1, total=len(ids),
                      score=session.get("score", 0), csrf=csrf_token(),
                      error="Please select one of the listed answers.")
    correct = chosen == question["answer"]
    if correct:
        session["score"] = session.get("score", 0) + 100
        session["correct_count"] = session.get("correct_count", 0) + 1
    session["answered"] = answered + [pos]
    session["last_correct"] = correct
    session["last_question_id"] = question["id"]
    return redirect(url_for("feedback"))

@app.get("/feedback")
def feedback():
    ids = session.get("round")
    pos = session.get("position")
    if not ids or pos is None or pos >= len(ids) or pos not in session.get("answered", []):
        return redirect(url_for("play"))
    question = next(q for q in QUESTIONS if q["id"] == session.get("last_question_id"))
    return render("feedback", question=question, index=pos+1, total=len(ids),
                  score=session.get("score", 0), correct=session.get("last_correct", False),
                  csrf=csrf_token())

@app.post("/next")
def next_question():
    if not valid_csrf():
        abort(400, "Invalid form token. Please refresh and try again.")
    ids = session.get("round")
    pos = session.get("position")
    if not ids or pos is None or pos not in session.get("answered", []):
        return redirect(url_for("play"))
    session["position"] = pos + 1
    if session["position"] >= len(ids):
        return redirect(url_for("finish"))
    return redirect(url_for("play"))

@app.get("/finish")
def finish():
    ids = session.get("round")
    if not ids or session.get("position", 0) < len(ids) or len(session.get("answered", [])) != len(ids):
        return redirect(url_for("play"))
    if not session.get("score_saved"):
        duration = max(1, min(3600, int(time.time() - session.get("started_at", time.time()))))
        with connect_db() as conn:
            conn.execute(
                "INSERT INTO scores (nickname, score, correct_count, total_questions, duration_seconds) VALUES (?, ?, ?, ?, ?)",
                (session.get("nickname", "Player"), int(session.get("score", 0)),
                 int(session.get("correct_count", 0)), len(ids), duration)
            )
        session["score_saved"] = True
    return render("result", score=session.get("score", 0),
                  correct_count=session.get("correct_count", 0), total=len(ids))

@app.get("/leaderboard")
def leaderboard():
    with connect_db() as conn:
        scores = conn.execute(
            "SELECT nickname, score, duration_seconds, created_at FROM scores ORDER BY score DESC, duration_seconds ASC, created_at ASC LIMIT 50"
        ).fetchall()
    return render("leaderboard", scores=scores)

@app.errorhandler(400)
def bad_request(error):
    return str(error), 400

if __name__ == "__main__":
    # Local only. Production hosting runs the app with gunicorn.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
