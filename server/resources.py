# server/resources.py
from models import db, User, Recipe

def create_user(username, password="secret123", image_url="", bio=""):
    """Create a user and commit to DB with a hashed password."""
    user = User(username=username, image_url=image_url, bio=bio)
    user.password_hash = password  # IMPORTANT: sets _password_hash
    db.session.add(user)
    db.session.commit()
    return user

def create_recipe(user, title, instructions, minutes_to_complete):
    """Create a recipe for a user and commit to DB."""
    recipe = Recipe(
        title=title,
        instructions=instructions,
        minutes_to_complete=minutes_to_complete,
        user=user  # associate recipe with user
    )
    db.session.add(recipe)
    db.session.commit()
    return recipe
