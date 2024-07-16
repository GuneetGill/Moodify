from flask import Flask
from dotenv import load_dotenv
import os
from routes import main_bp

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.urandom(64)

# Register blueprint
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
