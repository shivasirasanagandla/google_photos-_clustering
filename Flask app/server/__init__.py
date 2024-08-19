from flask import Flask
import os
app = Flask(__name__)

# Import configuration from config.py
app.config.from_pyfile('config.py')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import routes
from server import routes
