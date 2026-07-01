from app import app
from models import db, Promotion
from datetime import datetime, date

def add_demo_promotion():
    with app.app_context():
        # Check if demo promotion already exists
        existing = Promotion.query.filter_by(title='Summer Hair Care Special').first()
        if existing:
            print("Demo promotion already exists!")
            return
        
        # Create demo promotion
        demo_promotion = Promotion(
            title='Summer Hair Care Special',
            description='Get 20% off on all hair treatments this summer! Includes hair spa, deep conditioning, and keratin treatments. Limited time offer - book your appointment now!',
            image_url='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800',
            discount_percentage=20,
            valid_from=date(2024, 6, 1),
            valid_until=date(2024, 8, 31),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(demo_promotion)
        db.session.commit()
        print("Demo promotion added successfully!")
        print(f"Title: {demo_promotion.title}")
        print(f"Discount: {demo_promotion.discount_percentage}%")
        print(f"Valid: {demo_promotion.valid_from} to {demo_promotion.valid_until}")

if __name__ == '__main__':
    add_demo_promotion()
