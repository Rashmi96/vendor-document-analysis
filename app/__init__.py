from flask import Flask
from app.config import Config
from app.api import routes
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
from app.api.routes import main as main_blueprint  # Import the blueprint
app.register_blueprint(main_blueprint)

