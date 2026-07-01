from app import app
from models import db, Service, Stylist, Gallery, Testimonial, User, SiteSettings, About
from werkzeug.security import generate_password_hash

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Clear existing data (for re-initialization)
        Service.query.delete()
        Stylist.query.delete()
        Gallery.query.delete()
        Testimonial.query.delete()
        User.query.delete()
        SiteSettings.query.delete()
        About.query.delete()
        
        # Create admin user
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            email='admin@ashabeautysalon.com',
            is_admin=True
        )
        db.session.add(admin)
        
        # Create Services
        services = [
            Service(
                name='Layer Cut',
                description='A classic layered haircut that adds movement and volume to your hair. Perfect for all hair types and face shapes.',
                price=3500.00,
                duration='45 mins',
                image='https://images.unsplash.com/photo-1605497788044-5a32c7078486?w=600',
                category='haircut',
                featured=True
            ),
            Service(
                name='Butterfly Cut',
                description='Trendy butterfly cut that creates a beautiful, face-framing effect. Ideal for medium to long hair.',
                price=4500.00,
                duration='60 mins',
                image='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600',
                category='haircut',
                featured=True
            ),
            Service(
                name='Feather Cut',
                description='Soft, feathered layers that give a natural, airy look. Great for adding texture and dimension.',
                price=4000.00,
                duration='50 mins',
                image='https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=600',
                category='haircut',
                featured=True
            ),
            Service(
                name='Bob Cut',
                description='Timeless bob cut that never goes out of style. Available in various lengths from chin to shoulder.',
                price=3000.00,
                duration='40 mins',
                image='https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?w=600',
                category='haircut',
                featured=True
            ),
            Service(
                name='Hair Coloring',
                description='Professional hair coloring services including highlights, balayage, ombre, and full color transformations.',
                price=10000.00,
                duration='120 mins',
                image='https://images.unsplash.com/photo-1562322140-8baeececf3df?w=600',
                category='coloring',
                featured=True
            ),
            Service(
                name='Hair Spa',
                description='Rejuvenating hair spa treatment that nourishes and revitalizes your hair. Includes deep conditioning and massage.',
                price=2500.00,
                duration='45 mins',
                image='https://images.unsplash.com/photo-1519415510236-718bdfcd89c8?w=600',
                category='spa',
                featured=True
            ),
            Service(
                name='Step Cut',
                description='Structured step cut that creates defined layers. Perfect for adding volume and shape to your hair.',
                price=3800.00,
                duration='50 mins',
                image='https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=600',
                category='haircut',
                featured=False
            ),
            Service(
                name='U Cut',
                description='Elegant U-shaped cut that adds softness and movement. Great for long hair with a natural flow.',
                price=4200.00,
                duration='55 mins',
                image='https://images.unsplash.com/photo-1492106087820-71f1a00d2b11?w=600',
                category='haircut',
                featured=False
            ),
            Service(
                name='V Cut',
                description='Sharp V-shaped cut that creates a dramatic, stylish look. Ideal for those wanting a bold statement.',
                price=4500.00,
                duration='55 mins',
                image='https://images.unsplash.com/photo-1554519515-242161756769?w=600',
                category='haircut',
                featured=False
            ),
            Service(
                name='Hair Trim',
                description='Quick hair trim to maintain your current style and remove split ends. Essential for healthy hair.',
                price=1500.00,
                duration='30 mins',
                image='https://images.unsplash.com/photo-1620331311520-246422fd82f9?w=600',
                category='haircut',
                featured=False
            ),
            Service(
                name='Keratin Treatment',
                description='Professional keratin treatment that smooths and straightens hair while reducing frizz for months.',
                price=15000.00,
                duration='180 mins',
                image='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600',
                category='treatment',
                featured=False
            ),
            Service(
                name='Smoothening',
                description='Hair smoothening treatment that tames frizz and adds shine. Leaves hair silky and manageable.',
                price=12000.00,
                duration='150 mins',
                image='https://images.unsplash.com/photo-1560066984-138dadb4c035?w=600',
                category='treatment',
                featured=False
            ),
            Service(
                name='Bridal Hairstyle',
                description='Exquisite bridal hairstyling for your special day. Includes consultation, trial, and final styling.',
                price=20000.00,
                duration='120 mins',
                image='https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=600',
                category='styling',
                featured=False
            )
        ]
        
        for service in services:
            db.session.add(service)
        
        # Create Stylists
        stylists = [
            Stylist(
                name='Priya Sharma',
                specialization='Hair Coloring & Highlights',
                experience='8 years',
                image='https://images.unsplash.com/photo-1580489944761-15a19d654956?w=600',
                bio='Priya is a master colorist with expertise in balayage, ombre, and creative color techniques. She has trained internationally and brings the latest trends to our salon.'
            ),
            Stylist(
                name='Ananya Patel',
                specialization='Precision Haircuts',
                experience='6 years',
                image='https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=600',
                bio='Ananya specializes in precision cutting and textured hairstyles. Her attention to detail ensures every cut is perfectly tailored to each client.'
            ),
            Stylist(
                name='Meera Reddy',
                specialization='Hair Treatments & Spa',
                experience='10 years',
                image='https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=600',
                bio='Meera is our treatment specialist with extensive knowledge of hair health. She creates personalized treatment plans for damaged and chemically treated hair.'
            ),
            Stylist(
                name='Kavita Singh',
                specialization='Bridal & Event Styling',
                experience='7 years',
                image='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600',
                bio='Kavita is our bridal styling expert. She creates stunning, long-lasting hairstyles for weddings and special occasions, ensuring you look picture-perfect.'
            )
        ]
        
        for stylist in stylists:
            db.session.add(stylist)
        
        # Create Gallery Items
        gallery_items = [
            Gallery(
                title='Butterfly Cut',
                image='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600',
                category='haircut',
                description='Beautiful butterfly cut with soft layers'
            ),
            Gallery(
                title='Feather Cut',
                image='https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?w=600',
                category='haircut',
                description='Elegant feather cut for natural movement'
            ),
            Gallery(
                title='Layer Cut',
                image='https://images.unsplash.com/photo-1605497788044-5a32c7078486?w=600',
                category='haircut',
                description='Classic layered cut with volume'
            ),
            Gallery(
                title='Bob Cut',
                image='https://images.unsplash.com/photo-1560066984-138dadb4c035?w=600',
                category='haircut',
                description='Timeless bob cut style'
            ),
            Gallery(
                title='Step Cut',
                image='https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=600',
                category='haircut',
                description='Structured step cut layers'
            ),
            Gallery(
                title='Curtain Bangs',
                image='https://images.unsplash.com/photo-1492106087820-71f1a00d2b11?w=600',
                category='haircut',
                description='Trendy curtain bangs style'
            ),
            Gallery(
                title='Korean Layer Cut',
                image='https://images.unsplash.com/photo-1554519515-242161756769?w=600',
                category='haircut',
                description='Korean-inspired layered cut'
            ),
            Gallery(
                title='Shoulder Length Haircut',
                image='https://images.unsplash.com/photo-1620331311520-246422fd82f9?w=600',
                category='haircut',
                description='Versatile shoulder length cut'
            )
        ]
        
        for item in gallery_items:
            db.session.add(item)
        
        # Create Testimonials
        testimonials = [
            Testimonial(
                customer_name='Riya Gupta',
                customer_image='https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200',
                review='Absolutely love my new hair color! Priya did an amazing job with the balayage. The salon atmosphere is so relaxing and luxurious.',
                rating=5
            ),
            Testimonial(
                customer_name='Sneha Kapoor',
                customer_image='https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200',
                review='Best haircut I have ever had! Anaya really understood what I wanted and gave me the perfect layered cut. Will definitely be coming back.',
                rating=5
            ),
            Testimonial(
                customer_name='Pooja Verma',
                customer_image='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200',
                review='The hair spa treatment was divine. My hair feels so soft and healthy now. Meera is incredibly knowledgeable about hair care.',
                rating=5
            ),
            Testimonial(
                customer_name='Neha Sharma',
                customer_image='https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200',
                review='Kavita did my bridal hairstyle and it was absolutely perfect! She was so patient and made sure everything was exactly how I wanted it.',
                rating=5
            ),
            Testimonial(
                customer_name='Divya Mehta',
                customer_image='https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200',
                review='The keratin treatment transformed my hair completely. No more frizz and it is so smooth. Worth every penny!',
                rating=5
            ),
            Testimonial(
                customer_name='Anjali Singh',
                customer_image='https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=200',
                review='Such a wonderful experience from start to finish. The staff is professional, the salon is beautiful, and the results are amazing.',
                rating=5
            )
        ]
        
        for testimonial in testimonials:
            db.session.add(testimonial)
        
        # Create Site Settings
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
        
        # Create About Section
        about = About(
            title='About ASHA Beauty Salon',
            description='ASHA Beauty Salon has been a beacon of elegance and style in the beauty industry for over 15 years. Our journey began with a simple vision: to create a space where every client feels like royalty and leaves feeling more beautiful than when they arrived.',
            image='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800',
            years_experience=15,
            happy_clients=5000,
            expert_stylists=12
        )
        db.session.add(about)
        
        # Commit all changes
        db.session.commit()
        
        print("Database initialized successfully!")
        print("Admin login:")
        print("Username: admin")
        print("Password: admin123")

if __name__ == '__main__':
    init_database()
