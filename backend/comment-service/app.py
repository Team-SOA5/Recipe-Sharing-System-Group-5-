from flask import Flask, request, jsonify
from extensions import mongo, db
from routes import bp
from config import Config


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    db.init_app(app)
    # mongo.init_app(app)
    app.register_blueprint(bp)
    return app


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.create_all()

    app.run(debug=True)
