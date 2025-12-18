from flask_pymongo import PyMongo

# Initialize extensions
mongo = PyMongo()


def init_extensions(app):
    """Initialize Flask extensions"""
    mongo.init_app(app)
