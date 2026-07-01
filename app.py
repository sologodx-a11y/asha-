from flask import Flask, render_template
from models import db
from routes import init_routes
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///salon.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Domain configuration for production
# Uncomment and update these when deploying with your domain
# app.config['SERVER_NAME'] = 'ashabeautyparlour.qzz.io'
# app.config['SESSION_COOKIE_DOMAIN'] = 'ashabeautyparlour.qzz.io'
# app.config['PREFERRED_URL_SCHEME'] = 'https'

db.init_app(app)
init_routes(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # For production, set debug=False and use a production WSGI server like gunicorn
    app.run(debug=False, host='0.0.0.0', port=5000)
