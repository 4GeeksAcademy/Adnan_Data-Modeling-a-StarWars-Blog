
import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS

from src.utils import APIException, generate_sitemap
from src.admin import setup_admin
from src.models import db



def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace("postgres://", "postgresql://")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("FLASK_APP_KEY", "any key works")

    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    setup_admin(app)

    # -------------------------
    # Errors
    # -------------------------
    @app.errorhandler(APIException)
    def handle_invalid_usage(error):
        return jsonify(error.to_dict()), error.status_code

    # -------------------------
    # Routes
    # -------------------------
    @app.route("/")
    def sitemap():
        return generate_sitemap(app)

    # Optional health check
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    return app


app = create_app()

# Only runs when: python src/app.py
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=True)


# ---------------------------------------------------------
# Diagram generation:
# Running `pipenv run diagram` will produce diagram.png
# in the repository root.
# ---------------------------------------------------------
if __name__ == "__main__":
    from eralchemy2 import render_er
    import os

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(ROOT_DIR, "diagram.png")

    render_er(db.Model, out_path)
    print(f"✅ diagram generated at: {out_path}")
