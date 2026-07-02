from flask import Flask, render_template
from models import db, Service, Stylist, Gallery, Testimonial, User, SiteSettings, About
from routes import init_routes
from werkzeug.security import generate_password_hash
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

# Create database tables and initialize data on startup
with app.app_context():
    db.create_all()
    
    # Check if admin user exists, if not create it
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            email='admin@ashabeautysalon.com',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
    
    # Check if services exist, if not create sample data
    if Service.query.count() == 0:
        services = [
            Service(
                name='Layer Cut',
                description='A classic layered haircut that adds movement and volume to your hair.',
                price=3500.00,
                duration='45 mins',
                image='https://images.unsplash.com/photo-1605497788044-5a32c7078486?w=600',
                category='haircut',
                featured=True
            ),
            Service(
                name='Butterfly Cut',
                description='Trendy butterfly cut that creates a beautiful, face-framing effect.',
                price=4500.00,
                duration='60 mins',
                image='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600',
                category='haircut',
                featured=True
            ),
            Service(
                name='Hair Coloring',
                description='Professional hair coloring services including highlights and balayage.',
                price=10000.00,
                duration='120 mins',
                image='https://images.unsplash.com/photo-1562322140-8baeececf3df?w=600',
                category='coloring',
                featured=True
            ),
            Service(
                name='Hair Spa',
                description='Rejuvenating hair spa treatment that nourishes and revitalizes your hair.',
                price=2500.00,
                duration='45 mins',
                image='https://images.unsplash.com/photo-1519415510236-718bdfcd89c8?w=600',
                category='spa',
                featured=True
            )
        ]
        for service in services:
            db.session.add(service)
        db.session.commit()
    
    # Check if site settings exist
    if not SiteSettings.query.first():
        site_settings = SiteSettings(
            site_name='ASHA Beauty Salon',
            logo_url='https://via.placeholder.com/150x50?text=ASHA',
            phone='+91 98765 43210',
            email='info@ashabeautysalon.com',
            address='123 Beauty Street, Fashion District',
            whatsapp_number='919876543210',
            business_hours='Mon-Sat: 9AM - 8PM'
        )
        db.session.add(site_settings)
        db.session.commit()
    
    # Check if about section exists
    if not About.query.first():
        about = About(
            title='About ASHA Beauty Salon',
            description='ASHA Beauty Salon has been a beacon of elegance and style in the beauty industry for over 15 years.',
            image='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800',
            years_experience=15,
            happy_clients=5000,
            expert_stylists=12
        )
        db.session.add(about)
        db.session.commit()

if __name__ == '__main__':
    # For production, set debug=False and use a production WSGI server like gunicorn
    app.run(debug=False, host='0.0.0.0', port=5000)
