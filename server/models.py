from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import bcrypt

db = SQLAlchemy()

class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=True)  # <-- changed from False to True
    image_url = db.Column(db.String, default="")
    bio = db.Column(db.String, default="")

    # Relationship
    recipes = db.relationship(
        "Recipe", back_populates="user", cascade="all, delete-orphan"
    )

    # Avoid recursion when serializing
    serialize_rules = ("-recipes.user",)

    # Prevent reading the password hash
    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    # Setter hashes password
    @password_hash.setter
    def password_hash(self, password):
        # password should be plain string
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Authenticate helper
    def authenticate(self, password):
        if not self._password_hash:
            return False
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates("username")
    def validate_username(self, key, username):
        if not username or username.strip() == "":
            raise ValueError("Username must be present.")
        return username


class Recipe(db.Model, SerializerMixin):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # relationship
    user = db.relationship("User", back_populates="recipes")

    # Avoid recursion when serializing
    serialize_rules = ("-user.recipes",)

    @validates("title")
    def validate_title(self, key, title):
        if not title or title.strip() == "":
            raise ValueError("Title must be present.")
        return title

    @validates("instructions")
    def validate_instructions(self, key, instructions):
        if not instructions or instructions.strip() == "":
            raise ValueError("Instructions must be present.")
        if len(instructions.strip()) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions
