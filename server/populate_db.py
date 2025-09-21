# populate_db.py
from app import app, db
from models import User, Recipe

with app.app_context():
    # Clear existing data
    Recipe.query.delete()
    User.query.delete()
    db.session.commit()

    # Create a test user
    u = User(username="Prabhdip")
    u.password_hash = "secret123"  # VERY important! Sets _password_hash
    db.session.add(u)
    db.session.commit()

    # Create test recipes and associate them with the user
    r1 = Recipe(
        title="Delicious Shed Ham",
        instructions=(
            "Or kind rest bred with am shed then. In raptures building an bringing be. "
            "Elderly is detract tedious assured private so to visited. Do travelling "
            "companions contrasted it. Mistress strongly remember up to. Ham him compass "
            "you proceed calling detract. Better of always missed we person mr. September "
            "smallness northward situation few her certainty something."
        ),
        minutes_to_complete=60,
        user=u
    )

    r2 = Recipe(
        title="Hasty Party Ham",
        instructions=(
            "As am hastily invited settled at limited civilly fortune me. Really spring in "
            "extent an by. Judge but built gay party world. Of so am he remember although "
            "required. Bachelor unpacked be advanced at. Confined in declared marianne is vicinity."
        ),
        minutes_to_complete=30,
        user=u
    )

    db.session.add_all([r1, r2])
    db.session.commit()

    print("Database populated successfully!")
