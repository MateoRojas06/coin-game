import os
import secrets
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
