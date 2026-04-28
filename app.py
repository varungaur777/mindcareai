from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mindcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood_score = db.Column(db.Integer, nullable=False)
    mood_label = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.before_first_request
def create_tables():
    db.create_all()


def classify_mood(score: int) -> str:
    if score >= 80:
        return "Very Happy"
    elif score >= 60:
        return "Happy"
    elif score >= 40:
        return "Neutral"
    elif score >= 20:
        return "Stressed"
    else:
        return "Anxious"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/mood", methods=["GET", "POST"])
def mood():
    if request.method == "POST":
        try:
            q1 = int(request.form.get("q1", 0))
            q2 = int(request.form.get("q2", 0))
            q3 = int(request.form.get("q3", 0))
            q4 = int(request.form.get("q4", 0))
            q5 = int(request.form.get("q5", 0))
        except ValueError:
            q1 = q2 = q3 = q4 = q5 = 0

        total = q1 + q2 + q3 + q4 + q5  # max 25
        score = int((total / 25) * 100) if total > 0 else 0
        label = classify_mood(score)

        entry = MoodEntry(mood_score=score, mood_label=label)
        db.session.add(entry)
        db.session.commit()

        return render_template("mood.html", result=True, score=score, label=label)

    return render_template("mood.html", result=False)


@app.route("/chat")
def chat():
    return render_template("chatbot.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    user_message = (data.get("message") or "").lower()

    if any(word in user_message for word in ["stress", "stressed", "pressure", "overwhelmed"]):
        reply = (
            "It sounds like you're feeling stressed. "
            "Try a short breathing exercise: inhale for 4 seconds, hold for 4, exhale for 6. "
            "You can also take a 5-minute break away from screens."
        )
    elif any(word in user_message for word in ["anxiety", "anxious", "panic"]):
        reply = (
            "Anxiety can feel very intense. "
            "Notice 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste. "
            "Grounding can help bring you back to the present moment."
        )
    elif any(word in user_message for word in ["sad", "down", "low", "depressed"]):
        reply = (
            "I'm sorry you're feeling low. "
            "It might help to write down how you feel in the journal section, "
            "or reach out to someone you trust. You don't have to go through this alone."
        )
    elif any(word in user_message for word in ["happy", "good", "great", "fine"]):
        reply = (
            "I'm glad to hear that! "
            "You can still use the mood assessment and journal to track what’s working well for you."
        )
    elif "sleep" in user_message:
        reply = (
            "Sleep is very important for mental health. "
            "Try to keep a consistent sleep schedule and avoid screens 30 minutes before bed."
        )
    else:
        reply = (
            "Thank you for sharing. I’m a simple mental wellness assistant, not a therapist, "
            "but I can suggest breathing exercises, journaling, or mood tracking. "
            "If you're ever in serious distress, please reach out to a trusted person or professional."
        )

    return jsonify({"reply": reply})


@app.route("/dashboard")
def dashboard():
    entries = MoodEntry.query.order_by(MoodEntry.created_at.asc()).all()
    labels = [e.created_at.strftime("%d %b") for e in entries]
    scores = [e.mood_score for e in entries]
    mood_counts = {}
    for e in entries:
        mood_counts[e.mood_label] = mood_counts.get(e.mood_label, 0) + 1

    return render_template(
        "dashboard.html",
        labels=labels,
        scores=scores,
        mood_counts=mood_counts
    )


@app.route("/journal", methods=["GET", "POST"])
def journal():
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            entry = JournalEntry(content=content)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("journal"))

    entries = JournalEntry.query.order_by(JournalEntry.created_at.desc()).all()
    return render_template("journal.html", entries=entries)


@app.route("/meditation")
def meditation():
    suggestions = [
        {
            "title": "5-Minute Breathing Exercise",
            "description": "Focus on slow, deep breaths to calm your nervous system.",
            "link": "https://www.youtube.com/watch?v=SEfs5TJZ6Nk"
        },
        {
            "title": "Guided Body Scan",
            "description": "Gently notice sensations in your body from head to toe.",
            "link": "https://www.youtube.com/watch?v=QS2yDmWk0vs"
        },
        {
            "title": "Mindful Music",
            "description": "Soft ambient music to help you relax and unwind.",
            "link": "https://www.youtube.com/watch?v=2OEL4P1Rz04"
        }
    ]
    return render_template("meditation.html", suggestions=suggestions)


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
