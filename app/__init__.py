from flask import Flask
import os
  
def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.urandom(16)
    # Set other configuration options as needed

    # Register blueprints or import routes
    # Import the routes module or register blueprints here

    return app

app = create_app()
from app import routes