from flask import Flask, jsonify
from flask_cors import CORS

from config import Config

from models import db

from routes import api

# Creates and configures Flask app
def create_app() -> Flask:

    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize SQLAlchemy 
    db.init_app(app)

    # Enable CORS for API routes
    # Allows React frontend to access backend APIs
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"]
            }
        }
    )

    # Register API blueprint
    # All routes inside routes.py will start with /api
    app.register_blueprint(api, url_prefix="/api")

    # Ensure tables exist for local development/demo usage.
    with app.app_context():
        db.create_all()

    # HEALTH CHECK ROUTE
    # Used to check if backend server is running
    @app.get("/health")
    def health() -> dict:
        return {
            "success": True,
            "message": "ok"
        }

    # 404 ERROR HANDLER
    # Runs when route does not exist
    @app.errorhandler(404)
    def not_found(_error):

        return jsonify({
            "success": False,
            "message": "not found"
        }), 404

    # 500 ERROR HANDLER
    # Runs when internal server error occurs
    @app.errorhandler(500)
    def server_error(_error):

        return jsonify({
            "success": False,
            "message": "internal server error"
        }), 500

    # Creates all database tables
    @app.cli.command("init-db")
    def init_db() -> None:
        db.create_all()

        print(" Database tables created successfully!")

    return app

app = create_app()


# RUN FLASK DEVELOPMENT SERVER
if __name__ == "__main__":
    app.run(debug=True)