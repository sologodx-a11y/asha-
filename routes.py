from flask import render_template, redirect, url_for, flash, request, session
from models import db, Service, Stylist, Gallery, Testimonial, Appointment, User, About, SiteSettings, BeforeAfter, Promotion
from forms import AppointmentForm, ServiceForm, StylistForm, GalleryForm, LoginForm, ContactForm, AboutForm, TestimonialForm, SiteSettingsForm, BeforeAfterForm, PromotionForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app):
    
    @app.context_processor
    def inject_promotion_count():
        active_promotions_count = Promotion.query.filter_by(is_active=True).count()
        return dict(active_promotions_count=active_promotions_count)
    
    @app.route('/')
    def home():
        featured_services = Service.query.filter_by(featured=True).limit(6).all()
        gallery_images = Gallery.query.limit(8).all()
        stylists = Stylist.query.limit(4).all()
        testimonials = Testimonial.query.limit(6).all()
        about = About.query.first()
        site_settings = SiteSettings.query.first()
        before_after_images = BeforeAfter.query.filter_by(featured=True).limit(5).all()
        return render_template('index.html',
                             featured_services=featured_services,
                             gallery_images=gallery_images,
                             stylists=stylists,
                             testimonials=testimonials,
                             about=about,
                             site_settings=site_settings,
                             before_after_images=before_after_images)
    
    @app.route('/offers')
    def offers():
        promotions = Promotion.query.filter_by(is_active=True).all()
        site_settings = SiteSettings.query.first()
        return render_template('offers.html', promotions=promotions, site_settings=site_settings)
    
    @app.route('/services')
    def services():
        services = Service.query.filter_by(featured=True).all()
        categories = db.session.query(Service.category).distinct().all()
        site_settings = SiteSettings.query.first()
        return render_template('services.html', services=services, categories=categories, site_settings=site_settings)
    
    @app.route('/service/<int:service_id>')
    def service_detail(service_id):
        service = Service.query.get_or_404(service_id)
        site_settings = SiteSettings.query.first()
        return render_template('service_detail.html', service=service, site_settings=site_settings)
    
    @app.route('/gallery')
    def gallery():
        gallery_items = Gallery.query.all()
        categories = db.session.query(Gallery.category).distinct().all()
        site_settings = SiteSettings.query.first()
        return render_template('gallery.html', gallery_items=gallery_items, categories=categories, site_settings=site_settings)
    
    @app.route('/team')
    def team():
        stylists = Stylist.query.all()
        site_settings = SiteSettings.query.first()
        return render_template('team.html', stylists=stylists, site_settings=site_settings)
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        site_settings = SiteSettings.query.first()
        return render_template('contact.html', form=form, site_settings=site_settings)
    
    @app.route('/booking', methods=['GET', 'POST'])
    def booking():
        form = AppointmentForm()
        form.service_id.choices = [(s.id, f"{s.name} - ₹{s.price}") for s in Service.query.all()]
        form.stylist_id.choices = [(0, 'No Preference')] + [(s.id, s.name) for s in Stylist.query.all()]
        
        if form.validate_on_submit():
            appointment = Appointment(
                name=form.name.data,
                phone=form.phone.data,
                email=form.email.data,
                service_id=form.service_id.data,
                stylist_id=form.stylist_id.data if form.stylist_id.data != 0 else None,
                date=form.date.data,
                time=form.time.data,
                notes=form.notes.data
            )
            db.session.add(appointment)
            db.session.commit()
            flash('Appointment booked successfully! We will confirm your booking shortly.', 'success')
            return redirect(url_for('home'))
        
        site_settings = SiteSettings.query.first()
        return render_template('booking.html', form=form, site_settings=site_settings)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                flash('Login successful!', 'success')
                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('home'))
            flash('Invalid username or password.', 'danger')
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))
    
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        total_appointments = Appointment.query.count()
        pending_appointments = Appointment.query.filter_by(status='pending').count()
        total_services = Service.query.count()
        total_gallery = Gallery.query.count()
        recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
        site_settings = SiteSettings.query.first()
        
        return render_template('admin/dashboard.html',
                             total_appointments=total_appointments,
                             pending_appointments=pending_appointments,
                             total_services=total_services,
                             total_gallery=total_gallery,
                             recent_appointments=recent_appointments,
                             site_settings=site_settings)
    
    @app.route('/admin/appointments')
    @admin_required
    def admin_appointments():
        appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
        site_settings = SiteSettings.query.first()
        return render_template('admin/appointments.html', appointments=appointments, site_settings=site_settings)
    
    @app.route('/admin/appointment/<int:appointment_id>/status/<status>')
    @admin_required
    def update_appointment_status(appointment_id, status):
        appointment = Appointment.query.get_or_404(appointment_id)
        appointment.status = status
        db.session.commit()
        flash(f'Appointment status updated to {status}.', 'success')
        return redirect(url_for('admin_appointments'))
    
    @app.route('/admin/appointment/<int:appointment_id>/delete')
    @admin_required
    def delete_appointment(appointment_id):
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully.', 'success')
        return redirect(url_for('admin_appointments'))
    
    @app.route('/admin/services')
    @admin_required
    def admin_services():
        services = Service.query.all()
        site_settings = SiteSettings.query.first()
        return render_template('admin/services.html', services=services, site_settings=site_settings)
    
    @app.route('/admin/service/add', methods=['GET', 'POST'])
    @admin_required
    def add_service():
        form = ServiceForm()
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.image_url.data
            if form.image_file.data:
                filename = secure_filename(form.image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'

            service = Service(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                duration=form.duration.data,
                image=image_url,
                category=form.category.data,
                featured=form.featured.data
            )
            db.session.add(service)
            db.session.commit()
            flash('Service added successfully!', 'success')
            return redirect(url_for('admin_services'))
        return render_template('admin/service_form.html', form=form, title='Add Service', site_settings=site_settings)
    
    @app.route('/admin/service/<int:service_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_service(service_id):
        service = Service.query.get_or_404(service_id)
        form = ServiceForm(obj=service)
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.image_url.data
            if form.image_file.data:
                filename = secure_filename(form.image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'
            elif not image_url:
                # Keep existing image if no new image provided
                image_url = service.image

            service.name = form.name.data
            service.description = form.description.data
            service.price = form.price.data
            service.duration = form.duration.data
            service.image = image_url
            service.category = form.category.data
            service.featured = form.featured.data
            db.session.commit()
            flash('Service updated successfully!', 'success')
            return redirect(url_for('admin_services'))
        return render_template('admin/service_form.html', form=form, title='Edit Service', site_settings=site_settings)
    
    @app.route('/admin/service/<int:service_id>/delete')
    @admin_required
    def delete_service(service_id):
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully.', 'success')
        return redirect(url_for('admin_services'))
    
    @app.route('/admin/gallery')
    @admin_required
    def admin_gallery():
        gallery_items = Gallery.query.all()
        site_settings = SiteSettings.query.first()
        return render_template('admin/gallery.html', gallery_items=gallery_items, site_settings=site_settings)
    
    @app.route('/admin/gallery/add', methods=['GET', 'POST'])
    @admin_required
    def add_gallery_item():
        form = GalleryForm()
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.image_url.data
            if form.image_file.data:
                filename = secure_filename(form.image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'

            gallery_item = Gallery(
                title=form.title.data,
                image=image_url,
                category=form.category.data,
                description=form.description.data
            )
            db.session.add(gallery_item)
            db.session.commit()
            flash('Gallery item added successfully!', 'success')
            return redirect(url_for('admin_gallery'))
        return render_template('admin/gallery_form.html', form=form, title='Add Gallery Item', site_settings=site_settings)
    
    @app.route('/admin/gallery/<int:gallery_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_gallery_item(gallery_id):
        gallery_item = Gallery.query.get_or_404(gallery_id)
        form = GalleryForm(obj=gallery_item)
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.image_url.data
            if form.image_file.data:
                filename = secure_filename(form.image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'
            elif not image_url:
                # Keep existing image if no new image provided
                image_url = gallery_item.image

            gallery_item.title = form.title.data
            gallery_item.image = image_url
            gallery_item.category = form.category.data
            gallery_item.description = form.description.data
            db.session.commit()
            flash('Gallery item updated successfully!', 'success')
            return redirect(url_for('admin_gallery'))
        return render_template('admin/gallery_form.html', form=form, title='Edit Gallery Item', site_settings=site_settings)
    
    @app.route('/admin/gallery/<int:gallery_id>/delete')
    @admin_required
    def delete_gallery_item(gallery_id):
        gallery_item = Gallery.query.get_or_404(gallery_id)
        db.session.delete(gallery_item)
        db.session.commit()
        flash('Gallery item deleted successfully.', 'success')
        return redirect(url_for('admin_gallery'))
    
    @app.route('/admin/stylists')
    @admin_required
    def admin_stylists():
        stylists = Stylist.query.all()
        site_settings = SiteSettings.query.first()
        return render_template('admin/stylists.html', stylists=stylists, site_settings=site_settings)
    
    @app.route('/admin/stylist/add', methods=['GET', 'POST'])
    @admin_required
    def add_stylist():
        form = StylistForm()
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.image_url.data
            # Check if a file was actually uploaded (not a string and has filename attribute)
            if form.image_file.data and not isinstance(form.image_file.data, str) and hasattr(form.image_file.data, 'filename'):
                filename = secure_filename(form.image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'

            stylist = Stylist(
                name=form.name.data,
                specialization=form.specialization.data,
                experience=form.experience.data,
                image=image_url,
                bio=form.bio.data
            )
            db.session.add(stylist)
            db.session.commit()
            flash('Stylist added successfully!', 'success')
            return redirect(url_for('admin_stylists'))
        return render_template('admin/stylist_form.html', form=form, title='Add Stylist', site_settings=site_settings)
    
    @app.route('/admin/stylist/<int:stylist_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_stylist(stylist_id):
        stylist = Stylist.query.get_or_404(stylist_id)
        form = StylistForm(obj=stylist)
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.image_url.data
            # Check if a file was actually uploaded (not a string and has filename attribute)
            if form.image_file.data and not isinstance(form.image_file.data, str) and hasattr(form.image_file.data, 'filename'):
                filename = secure_filename(form.image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'
            elif not image_url:
                # Keep existing image if no new image provided
                image_url = stylist.image

            stylist.name = form.name.data
            stylist.specialization = form.specialization.data
            stylist.experience = form.experience.data
            stylist.image = image_url
            stylist.bio = form.bio.data
            db.session.commit()
            flash('Stylist updated successfully!', 'success')
            return redirect(url_for('admin_stylists'))
        return render_template('admin/stylist_form.html', form=form, title='Edit Stylist', stylist=stylist, site_settings=site_settings)
    
    @app.route('/admin/stylist/<int:stylist_id>/delete')
    @admin_required
    def delete_stylist(stylist_id):
        stylist = Stylist.query.get_or_404(stylist_id)
        db.session.delete(stylist)
        db.session.commit()
        flash('Stylist deleted successfully.', 'success')
        return redirect(url_for('admin_stylists'))
    
    @app.route('/admin/about', methods=['GET', 'POST'])
    @admin_required
    def edit_about():
        about = About.query.first()
        site_settings = SiteSettings.query.first()
        if not about:
            about = About(
                title='About ASHA Beauty Salon',
                description='ASHA Beauty Salon has been a beacon of elegance and style in the beauty industry for over 15 years. Our journey began with a simple vision: to create a space where every client feels like royalty and leaves feeling more beautiful than when they arrived.',
                image='https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800',
                years_experience=15,
                happy_clients=5000,
                expert_stylists=12
            )
            db.session.add(about)
            db.session.commit()

        form = AboutForm(obj=about)
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.image_url.data
            if form.image_file.data:
                filename = secure_filename(form.image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'
            elif not image_url:
                # Keep existing image if no new image provided
                image_url = about.image

            # Handle video upload or URL
            video_url = form.video_url.data
            if form.video_file.data:
                filename = secure_filename(form.video_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.video_file.data.save(filepath)
                video_url = f'/static/uploads/{filename}'
            elif not video_url:
                # Keep existing video if no new video provided
                video_url = about.video_url

            about.title = form.title.data
            about.description = form.description.data
            about.image = image_url
            about.video_url = video_url
            about.use_video = form.use_video.data
            about.years_experience = form.years_experience.data
            about.happy_clients = form.happy_clients.data
            about.expert_stylists = form.expert_stylists.data
            db.session.commit()
            flash('About section updated successfully!', 'success')
            return redirect(url_for('edit_about'))
        return render_template('admin/about_form.html', form=form, title='Edit About Section', site_settings=site_settings)
    
    @app.route('/admin/testimonials')
    @admin_required
    def admin_testimonials():
        testimonials = Testimonial.query.all()
        site_settings = SiteSettings.query.first()
        return render_template('admin/testimonials.html', testimonials=testimonials, site_settings=site_settings)
    
    @app.route('/admin/testimonial/add', methods=['GET', 'POST'])
    @admin_required
    def add_testimonial():
        form = TestimonialForm()
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.customer_image_url.data
            if form.customer_image_file.data:
                filename = secure_filename(form.customer_image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.customer_image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'

            testimonial = Testimonial(
                customer_name=form.customer_name.data,
                customer_image=image_url,
                review=form.review.data,
                rating=form.rating.data
            )
            db.session.add(testimonial)
            db.session.commit()
            flash('Testimonial added successfully!', 'success')
            return redirect(url_for('admin_testimonials'))
        return render_template('admin/testimonial_form.html', form=form, title='Add Testimonial', site_settings=site_settings)
    
    @app.route('/admin/testimonial/<int:testimonial_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_testimonial(testimonial_id):
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        form = TestimonialForm(obj=testimonial)
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.customer_image_url.data
            if form.customer_image_file.data:
                filename = secure_filename(form.customer_image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.customer_image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'
            elif not image_url:
                # Keep existing image if no new image provided
                image_url = testimonial.customer_image

            testimonial.customer_name = form.customer_name.data
            testimonial.customer_image = image_url
            testimonial.review = form.review.data
            testimonial.rating = form.rating.data
            db.session.commit()
            flash('Testimonial updated successfully!', 'success')
            return redirect(url_for('admin_testimonials'))
        return render_template('admin/testimonial_form.html', form=form, title='Edit Testimonial', site_settings=site_settings)
    
    @app.route('/admin/testimonial/<int:testimonial_id>/delete')
    @admin_required
    def delete_testimonial(testimonial_id):
        testimonial = Testimonial.query.get_or_404(testimonial_id)
        db.session.delete(testimonial)
        db.session.commit()
        flash('Testimonial deleted successfully.', 'success')
        return redirect(url_for('admin_testimonials'))
    
    @app.route('/admin/site-settings', methods=['GET', 'POST'])
    @admin_required
    def edit_site_settings():
        site_settings = SiteSettings.query.first()
        if not site_settings:
            site_settings = SiteSettings(
                site_name='ASHA Beauty Salon',
                logo_url='https://via.placeholder.com/150x50?text=ASHA'
            )
            db.session.add(site_settings)
            db.session.commit()
        
        form = SiteSettingsForm(obj=site_settings)
        if form.validate_on_submit():
            # Handle logo upload or URL
            logo_url = form.logo_url.data
            if form.logo_file.data:
                filename = secure_filename(form.logo_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.logo_file.data.save(filepath)
                logo_url = f'/static/uploads/{filename}'
            elif not logo_url:
                # Keep existing logo if no new logo provided
                logo_url = site_settings.logo_url

            # Handle background image upload or URL
            background_url = form.background_url.data
            if form.background_file.data:
                filename = secure_filename(form.background_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.background_file.data.save(filepath)
                background_url = f'/static/uploads/{filename}'
            elif not background_url:
                # Keep existing background if no new background provided
                background_url = site_settings.background_image

            site_settings.site_name = form.site_name.data
            site_settings.logo_url = logo_url
            site_settings.background_image = background_url
            site_settings.phone = form.phone.data
            site_settings.email = form.email.data
            site_settings.address = form.address.data
            site_settings.whatsapp_number = form.whatsapp_number.data
            site_settings.business_hours = form.business_hours.data
            site_settings.facebook_url = form.facebook_url.data
            site_settings.instagram_url = form.instagram_url.data
            site_settings.twitter_url = form.twitter_url.data
            site_settings.pinterest_url = form.pinterest_url.data
            db.session.commit()
            flash('Site settings updated successfully!', 'success')
            return redirect(url_for('edit_site_settings'))
        return render_template('admin/site_settings_form.html', form=form, title='Edit Site Settings')
    
    @app.route('/admin/before-after')
    @admin_required
    def admin_before_after():
        before_after_items = BeforeAfter.query.all()
        site_settings = SiteSettings.query.first()
        return render_template('admin/before_after.html', before_after_items=before_after_items, site_settings=site_settings)
    
    @app.route('/admin/before-after/add', methods=['GET', 'POST'])
    @admin_required
    def add_before_after():
        form = BeforeAfterForm()
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle before image upload or URL
            before_image_url = form.before_image_url.data
            if form.before_image_file.data:
                filename = secure_filename(form.before_image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.before_image_file.data.save(filepath)
                before_image_url = f'/static/uploads/{filename}'

            # Handle after image upload or URL
            after_image_url = form.after_image_url.data
            if form.after_image_file.data:
                filename = secure_filename(form.after_image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.after_image_file.data.save(filepath)
                after_image_url = f'/static/uploads/{filename}'

            before_after = BeforeAfter(
                title=form.title.data,
                before_image=before_image_url,
                after_image=after_image_url,
                service_type=form.service_type.data,
                description=form.description.data,
                featured=form.featured.data
            )
            db.session.add(before_after)
            db.session.commit()
            flash('Before/After transformation added successfully!', 'success')
            return redirect(url_for('admin_before_after'))
        return render_template('admin/before_after_form.html', form=form, title='Add Before/After Transformation', site_settings=site_settings)
    
    @app.route('/admin/before-after/<int:ba_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_before_after(ba_id):
        before_after = BeforeAfter.query.get_or_404(ba_id)
        form = BeforeAfterForm(obj=before_after)
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle before image upload or URL
            before_image_url = form.before_image_url.data
            if form.before_image_file.data:
                filename = secure_filename(form.before_image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.before_image_file.data.save(filepath)
                before_image_url = f'/static/uploads/{filename}'
            elif not before_image_url:
                before_image_url = before_after.before_image

            # Handle after image upload or URL
            after_image_url = form.after_image_url.data
            if form.after_image_file.data:
                filename = secure_filename(form.after_image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.after_image_file.data.save(filepath)
                after_image_url = f'/static/uploads/{filename}'
            elif not after_image_url:
                after_image_url = before_after.after_image

            before_after.title = form.title.data
            before_after.before_image = before_image_url
            before_after.after_image = after_image_url
            before_after.service_type = form.service_type.data
            before_after.description = form.description.data
            before_after.featured = form.featured.data
            db.session.commit()
            flash('Before/After transformation updated successfully!', 'success')
            return redirect(url_for('admin_before_after'))
        return render_template('admin/before_after_form.html', form=form, title='Edit Before/After Transformation', site_settings=site_settings)
    
    @app.route('/admin/before-after/<int:ba_id>/delete')
    @admin_required
    def delete_before_after(ba_id):
        before_after = BeforeAfter.query.get_or_404(ba_id)
        db.session.delete(before_after)
        db.session.commit()
        flash('Before/After transformation deleted successfully.', 'success')
        return redirect(url_for('admin_before_after'))
    
    @app.route('/admin/promotions')
    @admin_required
    def admin_promotions():
        promotions = Promotion.query.all()
        site_settings = SiteSettings.query.first()
        return render_template('admin/promotions.html', promotions=promotions, site_settings=site_settings)
    
    @app.route('/admin/promotion/add', methods=['GET', 'POST'])
    @admin_required
    def add_promotion():
        form = PromotionForm()
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.image_url.data
            if form.image_file.data:
                filename = secure_filename(form.image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'

            promotion = Promotion(
                title=form.title.data,
                description=form.description.data,
                image_url=image_url,
                discount_percentage=form.discount_percentage.data,
                valid_from=form.valid_from.data,
                valid_until=form.valid_until.data,
                is_active=form.is_active.data
            )
            db.session.add(promotion)
            db.session.commit()
            flash('Promotion added successfully!', 'success')
            return redirect(url_for('admin_promotions'))
        return render_template('admin/promotion_form.html', form=form, title='Add Promotion', site_settings=site_settings)
    
    @app.route('/admin/promotion/<int:promo_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_promotion(promo_id):
        promotion = Promotion.query.get_or_404(promo_id)
        form = PromotionForm(obj=promotion)
        site_settings = SiteSettings.query.first()
        if form.validate_on_submit():
            # Handle image upload or URL
            image_url = form.image_url.data
            if form.image_file.data:
                filename = secure_filename(form.image_file.data.filename)
                upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.image_file.data.save(filepath)
                image_url = f'/static/uploads/{filename}'
            elif not image_url:
                image_url = promotion.image_url

            promotion.title = form.title.data
            promotion.description = form.description.data
            promotion.image_url = image_url
            promotion.discount_percentage = form.discount_percentage.data
            promotion.valid_from = form.valid_from.data
            promotion.valid_until = form.valid_until.data
            promotion.is_active = form.is_active.data
            db.session.commit()
            flash('Promotion updated successfully!', 'success')
            return redirect(url_for('admin_promotions'))
        return render_template('admin/promotion_form.html', form=form, title='Edit Promotion', site_settings=site_settings)
    
    @app.route('/admin/promotion/<int:promo_id>/delete')
    @admin_required
    def delete_promotion(promo_id):
        promotion = Promotion.query.get_or_404(promo_id)
        db.session.delete(promotion)
        db.session.commit()
        flash('Promotion deleted successfully.', 'success')
        return redirect(url_for('admin_promotions'))
