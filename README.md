# ASHA Beauty Salon Website

A complete production-ready hair salon website built with Python Flask, featuring a premium luxury design with elegant feminine aesthetics.

## Features

- **Beautiful Homepage** with 8 fully designed sections
- **Services Page** with detailed service listings
- **Gallery Page** showcasing hairstyles and transformations
- **Team Page** featuring expert stylists
- **Contact Page** with contact form and information
- **Booking System** for appointment scheduling
- **Admin Panel** for managing appointments, services, gallery, and stylists
- **Responsive Design** works perfectly on mobile, tablet, and desktop
- **Premium UI** with glassmorphism cards, smooth animations, and luxury styling

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Framework**: Bootstrap 5
- **Templating**: Jinja2
- **Forms**: Flask-WTF
- **ORM**: Flask-SQLAlchemy

## Project Structure

```
asha/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── routes.py              # Route handlers
├── forms.py               # Form classes
├── init_db.py            # Database initialization script
├── requirements.txt      # Python dependencies
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── services.html     # Services page
│   ├── gallery.html      # Gallery page
│   ├── team.html         # Team page
│   ├── contact.html      # Contact page
│   ├── booking.html      # Booking page
│   ├── login.html        # Admin login
│   └── admin/            # Admin panel templates
│       ├── dashboard.html
│       ├── appointments.html
│       ├── services.html
│       ├── gallery.html
│       ├── stylists.html
│       ├── service_form.html
│       ├── gallery_form.html
│       └── stylist_form.html
└── static/
    ├── css/
    │   └── style.css     # Custom styling
    ├── js/
    │   └── main.js       # JavaScript functionality
    ├── images/           # Image assets
    └── uploads/          # User uploads
```

## Installation

1. **Clone or download the project**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database with sample data**
   ```bash
   python init_db.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## Admin Access

After initializing the database, you can access the admin panel:

- **URL**: `http://localhost:5000/login`
- **Username**: `admin`
- **Password**: `admin123`

## Admin Features

- **Dashboard**: View statistics and recent appointments
- **Appointments**: Manage customer bookings (confirm, cancel, delete)
- **Services**: Add, edit, and delete salon services
- **Gallery**: Manage gallery images
- **Stylists**: Add, edit, and delete stylist profiles

## Database Tables

- **services**: Hair services with pricing and duration
- **stylists**: Salon staff information
- **gallery**: Hairstyle gallery images
- **testimonials**: Customer reviews
- **appointments**: Booking records
- **users**: Admin user accounts

## Design Features

- **Color Scheme**: Soft pink, white, cream, beige, and gold
- **Glassmorphism**: Modern glass-effect cards
- **Animations**: Smooth scroll and hover effects
- **Typography**: Playfair Display and Poppins fonts
- **Responsive**: Mobile-first design approach
- **Icons**: Font Awesome integration

## Sample Data Included

The database initialization script includes:

- **13 Services**: Layer Cut, Butterfly Cut, Feather Cut, Bob Cut, Hair Coloring, Hair Spa, and more
- **4 Stylists**: Complete with photos, specializations, and experience
- **8 Gallery Images**: Popular hairstyles with descriptions
- **6 Testimonials**: Customer reviews with ratings
- **1 Admin User**: For accessing the admin panel

## Customization

### Changing Colors

Edit `static/css/style.css` and modify the CSS variables at the top:

```css
:root {
    --primary-pink: #E8B4B8;
    --soft-pink: #F5D0D5;
    --cream: #FFF8F0;
    --beige: #F5E6D3;
    --gold: #D4AF37;
    /* ... more variables */
}
```

### Adding New Services

Access the admin panel at `/admin` and navigate to Services > Add New Service

### Modifying Content

All page content is in the `templates/` directory. Edit the respective HTML files to modify text, images, or structure.

## Security Notes

- Change the `SECRET_KEY` in `app.py` for production
- Change the admin password after first login
- Use environment variables for sensitive configuration
- Enable HTTPS in production

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

This project is for demonstration purposes. Feel free to modify and use for your own salon website.

## Support

For issues or questions, please refer to the Flask documentation and the technologies used in this project.
