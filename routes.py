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
    
    @app.route('/init-db')
    def init_database():
        """Initialize database with sample data"""
        from werkzeug.security import generate_password_hash
        
        # Create admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@ashabeautysalon.com',
                is_admin=True
            )
            db.session.add(admin)
        
        # Create Services
        if Service.query.count() == 0:
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
        if Stylist.query.count() == 0:
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
        if Gallery.query.count() == 0:
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
        if Testimonial.query.count() == 0:
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
        
        # Create About Section
        if not About.query.first():
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
        return "Database initialized successfully! <a href='/'>Go to Home</a>"
    
    @app.route('/import-data', methods=['GET', 'POST'])
    def import_data():
        """Import data from JSON file"""
        import json
        from werkzeug.security import generate_password_hash
        
        if request.method == 'POST':
            if 'file' not in request.files:
                return "No file uploaded"
            
            file = request.files['file']
            if file.filename == '':
                return "No file selected"
            
            if file and file.filename.endswith('.json'):
                try:
                    data = json.load(file)
                    
                    # Import Users
                    for user_data in data.get('users', []):
                        if not User.query.filter_by(username=user_data['username']).first():
                            user = User(
                                username=user_data['username'],
                                password=user_data['password'],
                                email=user_data['email'],
                                is_admin=user_data['is_admin']
                            )
                            db.session.add(user)
                    
                    # Import Services
                    for service_data in data.get('services', []):
                        if not Service.query.filter_by(name=service_data['name']).first():
                            service = Service(
                                name=service_data['name'],
                                description=service_data['description'],
                                price=service_data['price'],
                                duration=service_data['duration'],
                                image=service_data['image'],
                                category=service_data['category'],
                                featured=service_data['featured']
                            )
                            db.session.add(service)
                    
                    # Import Stylists
                    for stylist_data in data.get('stylists', []):
                        if not Stylist.query.filter_by(name=stylist_data['name']).first():
                            stylist = Stylist(
                                name=stylist_data['name'],
                                specialization=stylist_data['specialization'],
                                experience=stylist_data['experience'],
                                image=stylist_data['image'],
                                bio=stylist_data.get('bio')
                            )
                            db.session.add(stylist)
                    
                    # Import Gallery
                    for gallery_data in data.get('gallery', []):
                        if not Gallery.query.filter_by(title=gallery_data['title']).first():
                            gallery = Gallery(
                                title=gallery_data['title'],
                                image=gallery_data['image'],
                                category=gallery_data['category'],
                                description=gallery_data.get('description')
                            )
                            db.session.add(gallery)
                    
                    # Import Testimonials
                    for testimonial_data in data.get('testimonials', []):
                        if not Testimonial.query.filter_by(customer_name=testimonial_data['customer_name']).first():
                            testimonial = Testimonial(
                                customer_name=testimonial_data['customer_name'],
                                customer_image=testimonial_data['customer_image'],
                                review=testimonial_data['review'],
                                rating=testimonial_data['rating']
                            )
                            db.session.add(testimonial)
                    
                    # Import About
                    about_data = data.get('about')
                    if about_data and not About.query.first():
                        about = About(
                            title=about_data['title'],
                            description=about_data['description'],
                            image=about_data['image'],
                            video_url=about_data.get('video_url'),
                            use_video=about_data.get('use_video', False),
                            years_experience=about_data['years_experience'],
                            happy_clients=about_data['happy_clients'],
                            expert_stylists=about_data['expert_stylists']
                        )
                        db.session.add(about)
                    
                    # Import SiteSettings
                    settings_data = data.get('site_settings')
                    if settings_data and not SiteSettings.query.first():
                        settings = SiteSettings(
                            site_name=settings_data['site_name'],
                            logo_url=settings_data['logo_url'],
                            background_image=settings_data.get('background_image'),
                            phone=settings_data['phone'],
                            email=settings_data['email'],
                            address=settings_data['address'],
                            whatsapp_number=settings_data['whatsapp_number'],
                            business_hours=settings_data['business_hours'],
                            facebook_url=settings_data.get('facebook_url'),
                            instagram_url=settings_data.get('instagram_url'),
                            twitter_url=settings_data.get('twitter_url'),
                            pinterest_url=settings_data.get('pinterest_url')
                        )
                        db.session.add(settings)
                    
                    # Import BeforeAfter
                    for ba_data in data.get('before_after', []):
                        if not BeforeAfter.query.filter_by(title=ba_data['title']).first():
                            before_after = BeforeAfter(
                                title=ba_data['title'],
                                before_image=ba_data['before_image'],
                                after_image=ba_data['after_image'],
                                service_type=ba_data['service_type'],
                                description=ba_data.get('description'),
                                featured=ba_data['featured']
                            )
                            db.session.add(before_after)
                    
                    # Import Promotions
                    for promo_data in data.get('promotions', []):
                        if not Promotion.query.filter_by(title=promo_data['title']).first():
                            promotion = Promotion(
                                title=promo_data['title'],
                                description=promo_data['description'],
                                image_url=promo_data.get('image_url'),
                                discount_percentage=promo_data.get('discount_percentage'),
                                valid_from=promo_data.get('valid_from'),
                                valid_until=promo_data.get('valid_until'),
                                is_active=promo_data['is_active']
                            )
                            db.session.add(promotion)
                    
                    db.session.commit()
                    return "Data imported successfully! <a href='/'>Go to Home</a>"
                except Exception as e:
                    return f"Error importing data: {str(e)}"
            else:
                return "Please upload a JSON file"
        
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Import Data</title>
        </head>
        <body>
            <h1>Import Data from JSON</h1>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file" accept=".json" required>
                <button type="submit">Import</button>
            </form>
            <p><a href="/">Back to Home</a></p>
        </body>
        </html>
        '''
    
    @app.route('/export-data')
    def export_data():
        """Export data to JSON file"""
        import json
        from flask import Response
        
        data = {
            'users': [],
            'services': [],
            'stylists': [],
            'gallery': [],
            'testimonials': [],
            'about': None,
            'site_settings': None,
            'before_after': [],
            'promotions': []
        }
        
        # Export Users
        users = User.query.all()
        for user in users:
            data['users'].append({
                'username': user.username,
                'password': user.password,
                'email': user.email,
                'is_admin': user.is_admin
            })
        
        # Export Services
        services = Service.query.all()
        for service in services:
            data['services'].append({
                'name': service.name,
                'description': service.description,
                'price': service.price,
                'duration': service.duration,
                'image': service.image,
                'category': service.category,
                'featured': service.featured
            })
        
        # Export Stylists
        stylists = Stylist.query.all()
        for stylist in stylists:
            data['stylists'].append({
                'name': stylist.name,
                'specialization': stylist.specialization,
                'experience': stylist.experience,
                'image': stylist.image,
                'bio': stylist.bio
            })
        
        # Export Gallery
        gallery = Gallery.query.all()
        for item in gallery:
            data['gallery'].append({
                'title': item.title,
                'image': item.image,
                'category': item.category,
                'description': item.description
            })
        
        # Export Testimonials
        testimonials = Testimonial.query.all()
        for testimonial in testimonials:
            data['testimonials'].append({
                'customer_name': testimonial.customer_name,
                'customer_image': testimonial.customer_image,
                'review': testimonial.review,
                'rating': testimonial.rating
            })
        
        # Export About
        about = About.query.first()
        if about:
            data['about'] = {
                'title': about.title,
                'description': about.description,
                'image': about.image,
                'video_url': about.video_url,
                'use_video': about.use_video,
                'years_experience': about.years_experience,
                'happy_clients': about.happy_clients,
                'expert_stylists': about.expert_stylists
            }
        
        # Export SiteSettings
        settings = SiteSettings.query.first()
        if settings:
            data['site_settings'] = {
                'site_name': settings.site_name,
                'logo_url': settings.logo_url,
                'background_image': settings.background_image,
                'phone': settings.phone,
                'email': settings.email,
                'address': settings.address,
                'whatsapp_number': settings.whatsapp_number,
                'business_hours': settings.business_hours,
                'facebook_url': settings.facebook_url,
                'instagram_url': settings.instagram_url,
                'twitter_url': settings.twitter_url,
                'pinterest_url': settings.pinterest_url
            }
        
        # Export BeforeAfter
        before_after = BeforeAfter.query.all()
        for ba in before_after:
            data['before_after'].append({
                'title': ba.title,
                'before_image': ba.before_image,
                'after_image': ba.after_image,
                'service_type': ba.service_type,
                'description': ba.description,
                'featured': ba.featured
            })
        
        # Export Promotions
        promotions = Promotion.query.all()
        for promo in promotions:
            data['promotions'].append({
                'title': promo.title,
                'description': promo.description,
                'image_url': promo.image_url,
                'discount_percentage': promo.discount_percentage,
                'valid_from': str(promo.valid_from) if promo.valid_from else None,
                'valid_until': str(promo.valid_until) if promo.valid_until else None,
                'is_active': promo.is_active
            })
        
        json_str = json.dumps(data, indent=2, default=str)
        return Response(
            json_str,
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=data_export.json'}
        )
