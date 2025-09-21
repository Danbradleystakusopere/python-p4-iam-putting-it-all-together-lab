# server/app.py
from flask import Flask, request, jsonify, session, make_response
from flask_migrate import Migrate
from config import bcrypt
from models import db, User, Recipe

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# required for sessions
app.secret_key = "dev-secret-key-change-me"

# init extensions
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

# --- Helpers ---
def user_dict(user):
    # return only required fields for frontend/tests
    return {
        "id": user.id,
        "username": user.username,
        "image_url": user.image_url,
        "bio": user.bio,
    }

# --- Routes ---
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    image_url = data.get("image_url", "")
    bio = data.get("bio", "")

    # create user instance and catch validation errors
    try:
        user = User(username=username, image_url=image_url, bio=bio)
        # set hashed password via setter
        user.password_hash = password
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        # create a consistent errors array
        db.session.rollback()
        msg = str(e)
        return jsonify({"errors": [msg]}), 422

    # save user id in session (auto-login)
    session["user_id"] = user.id
    return jsonify(user_dict(user)), 201


@app.route("/check_session", methods=["GET"])
def check_session():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authorized"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Not authorized"}), 401

    return jsonify(user_dict(user)), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.authenticate(password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user.id
    return jsonify(user_dict(user)), 200


@app.route("/logout", methods=["DELETE"])
def logout():
    # ✅ FIX: handle both missing key and None value
    if not session.get("user_id"):
        return jsonify({"error": "Not authorized"}), 401

    session.pop("user_id", None)
    return ("", 204)


@app.route("/recipes", methods=["GET", "POST"])
def recipes_index_create():
    # GET -> list recipes (must be logged in)
    if request.method == "GET":
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Not authorized"}), 401

        recipes = Recipe.query.all()
        results = []
        for r in recipes:
            results.append({
                "id": r.id,
                "title": r.title,
                "instructions": r.instructions,
                "minutes_to_complete": r.minutes_to_complete,
                "user": {
                    "id": r.user.id,
                    "username": r.user.username,
                    "image_url": r.user.image_url,
                    "bio": r.user.bio,
                }
            })
        return jsonify(results), 200

    # POST -> create recipe (must be logged in)
    if request.method == "POST":
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Not authorized"}), 401

        data = request.get_json() or {}
        title = data.get("title")
        instructions = data.get("instructions")
        minutes_to_complete = data.get("minutes_to_complete")

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"errors": [str(e)]}), 422

        result = {
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "minutes_to_complete": recipe.minutes_to_complete,
            "user": {
                "id": recipe.user.id,
                "username": recipe.user.username,
                "image_url": recipe.user.image_url,
                "bio": recipe.user.bio,
            }
        }
        return jsonify(result), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
