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

MAX_USERNAME_LENGHT = 20
LEADERBOARD_LIMIT = 20

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "cambia-esto-en-produccion")

db_url = os.environ.get("DATABASE_URL", "sqlite:///ranking.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False)
    streak = db.Column(db.Integer, nullable = False)

with app.app_context():
    db.create_all()


# ROUTES START
@app.route("/", methods = ["GET"])
def index():
    render_template("index.html")