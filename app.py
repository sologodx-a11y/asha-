from flask import Flask, render_template
from models import db
from routes import init_routes
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Use PostgreSQL in production, SQLite in development
database_url = os.environ.get('DATABASE_URL', 'postgresql://admin:k5uVhCsXflGzxm0APNRX96p7FuXhMvyt@dpg-d92u8h9kh4rs7393uofg-a.singapore-postgres.render.com/salon_gqpw')
if database_url:
    # Fix PostgreSQL URL for SQLAlchemy and use psycopg3 driver
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
    elif database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///salon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Domain configuration for production
# Uncomment and update these when deploying with your domain
# app.config['SERVER_NAME'] = 'ashabeautyparlour.qzz.io'
# app.config['SESSION_COOKIE_DOMAIN'] = 'ashabeautyparlour.qzz.io'
# app.config['PREFERRED_URL_SCHEME'] = 'https'

db.init_app(app)
init_routes(app)

# Create database tables on startup (only tables, no data reset)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # For production, set debug=False and use a production WSGI server like gunicorn
    app.run(debug=True, host='0.0.0.0', port=5000)
