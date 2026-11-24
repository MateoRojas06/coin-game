import os
import secrets
from enum import IntEnum
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

load_dotenv()


class CoinSide(IntEnum):
    CARA = 0
    SELLO = 1


MAX_USERNAME_LENGHT: int = 20
LEADERBOARD_LIMIT: int = 20

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "cambia-esto-en-produccion")

db_url = os.environ.get("DATABASE_URL", "sqlite:///ranking.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    streak = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "username": self.username,
            "streak": self.streak
        }


with app.app_context():
    db.create_all()


# ROUTES START
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/flip", methods=["POST"])
def flip():
    data = request.get_json(silent=True)
    raw_guess = data.get("guess")

    if (type(raw_guess) is not int or
       raw_guess not in (CoinSide.CARA, CoinSide.SELLO)):
        return jsonify({
            "error": "guess must be 0 or 1"
        }), 400

    win: bool = False
    guess: CoinSide = CoinSide(raw_guess)
    result: CoinSide = secrets.choice(list(CoinSide))
    current_streak: int = session.get("streak", 0)
    final_streak: int = 0

    if guess == result:
        current_streak += 1
        session["streak"] = current_streak
        win = True
    else:
        if current_streak > 1:
            final_streak = current_streak
        if current_streak > session.get("max_streak", 0):
            session["max_streak"] = current_streak
        session["streak"] = 0
        current_streak = session["streak"]

    data_result = {
        "win": win,
        "streak": current_streak,
        "result": int(result),
    }
    if final_streak != 0:
        data_result["final_streak"] = final_streak
        data_result["max_streak"] = session.get("max_streak", 0)

    return jsonify(data_result)


@app.route("/save-score", methods=["POST"])
def save_score():
    data = request.get_json(silent=True)
    submited_score: int = session.get("max_streak", 0)
    username: str = (data.get("username") or "").strip()[:MAX_USERNAME_LENGHT]

    if username and submited_score != 0:
        db.session.add(Score(username=username, streak=submited_score))
        db.session.commit()
        return jsonify({"ok": True}), 201
    else:
        return jsonify({"error": "did not save score"}), 422


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    top_scores = (
        Score.query
        .order_by(Score.streak.desc())
        .limit(LEADERBOARD_LIMIT)
        .all
    )
    return jsonify(score.to_dict for score in top_scores)


if __name__ == "__main__":
    app.run(debug=True)
