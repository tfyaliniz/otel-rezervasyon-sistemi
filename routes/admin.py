from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models.room import Room, RoomImage
from models.reservation import Reservation, Payment
from models.user import User
from models.notification import MaintenanceRecord
from database import db
from datetime import datetime, timedelta
from sqlalchemy import func
import os

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Bu sayfaya erişim yetkiniz yok.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def dashboard():
    """Admin paneli ana sayfa"""
    # İstatistikleri hesapla
    total_rooms = Room.query.count()
    active_reservations = Reservation.query.filter(
        Reservation.status.in_(['pending', 'confirmed'])
    ).count()
    total_users = User.query.count()
    
    # Son 30 günlük gelir
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        Payment.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Son rezervasyonlar
    recent_reservations = Reservation.query.order_by(
        Reservation.created_at.desc()
    ).limit(5).all()
    
    # Bakım kayıtları
    maintenance_records = MaintenanceRecord.query.filter(
        MaintenanceRecord.status != 'completed'
    ).order_by(MaintenanceRecord.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_rooms=total_rooms,
                         active_reservations=active_reservations,
                         total_users=total_users,
                         total_revenue=total_revenue,
                         recent_reservations=recent_reservations,
                         maintenance_records=maintenance_records)

@admin.route('/rooms')
@login_required
@admin_required
def rooms():
    """Oda yönetimi"""
    rooms = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms)

@admin.route('/room/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_room():
    """Yeni oda ekle"""
    if request.method == 'POST':
        room = Room(
            room_number=request.form['room_number'],
            room_type=request.form['room_type'],
            capacity=int(request.form['capacity']),
            price=float(request.form['price']),
            floor=int(request.form['floor']),
            size=float(request.form['size']),
            description=request.form['description'],
            has_balcony=bool(request.form.get('has_balcony')),
            has_sea_view=bool(request.form.get('has_sea_view'))
        )
        db.session.add(room)
        db.session.commit()
        
        # Resimleri kaydet
        if 'images' in request.files:
            images = request.files.getlist('images')
            for image in images:
                if image and image.filename:
                    # Resmi kaydet
                    filename = f"{room.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
                    image.save(os.path.join('static/img/rooms', filename))
                    
                    # Veritabanına kaydet
                    room_image = RoomImage(
                        room_id=room.id,
                        image_path=filename
                    )
                    db.session.add(room_image)
            
            db.session.commit()
        
        flash('Oda başarıyla eklendi.', 'success')
        return redirect(url_for('admin.rooms'))
    
    return render_template('admin/add_room.html')

@admin.route('/room/<int:room_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_room(room_id):
    """Oda düzenle"""
    room = Room.query.get_or_404(room_id)
    
    if request.method == 'POST':
        room.room_number = request.form['room_number']
        room.room_type = request.form['room_type']
        room.capacity = int(request.form['capacity'])
        room.price = float(request.form['price'])
        room.floor = int(request.form['floor'])
        room.size = float(request.form['size'])
        room.description = request.form['description']
        room.has_balcony = bool(request.form.get('has_balcony'))
        room.has_sea_view = bool(request.form.get('has_sea_view'))
        room.is_active = bool(request.form.get('is_active'))
        
        # Yeni resimleri kaydet
        if 'images' in request.files:
            images = request.files.getlist('images')
            for image in images:
                if image and image.filename:
                    # Resmi kaydet
                    filename = f"{room.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
                    image.save(os.path.join('static/img/rooms', filename))
                    
                    # Veritabanına kaydet
                    room_image = RoomImage(
                        room_id=room.id,
                        image_path=filename
                    )
                    db.session.add(room_image)
        
        db.session.commit()
        flash('Oda başarıyla güncellendi.', 'success')
        return redirect(url_for('admin.rooms'))
    
    return render_template('admin/edit_room.html', room=room)

@admin.route('/room/image/<int:image_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_room_image(image_id):
    """Oda resmini sil"""
    image = RoomImage.query.get_or_404(image_id)
    
    # Dosyayı sil
    try:
        os.remove(os.path.join('static/img/rooms', image.image_path))
    except:
        pass
    
    # Veritabanından sil
    db.session.delete(image)
    db.session.commit()
    
    return jsonify({'success': True})

@admin.route('/room/<int:room_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    """Oda sil"""
    room = Room.query.get_or_404(room_id)
    
    # Resimleri sil
    for image in room.images:
        try:
            os.remove(os.path.join('static/img/rooms', image.image_path))
        except:
            pass
    
    db.session.delete(room)
    db.session.commit()
    
    flash('Oda başarıyla silindi.', 'success')
    return redirect(url_for('admin.rooms'))

@admin.route('/reservations')
@login_required
@admin_required
def reservations():
    """Rezervasyon yönetimi"""
    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = Reservation.query
    if status != 'all':
        query = query.filter_by(status=status)
    
    reservations = query.order_by(Reservation.created_at.desc()).paginate(
        page=page, per_page=10
    )
    
    return render_template('admin/reservations.html',
                         reservations=reservations,
                         current_status=status)

@admin.route('/reservation/<int:reservation_id>')
@login_required
@admin_required
def reservation_detail(reservation_id):
    """Rezervasyon detayı"""
    reservation = Reservation.query.get_or_404(reservation_id)
    return render_template('admin/reservation_detail.html', reservation=reservation)

@admin.route('/reservation/<int:reservation_id>/status', methods=['POST'])
@login_required
@admin_required
def update_reservation_status(reservation_id):
    """Rezervasyon durumunu güncelle"""
    reservation = Reservation.query.get_or_404(reservation_id)
    status = request.form.get('status')
    
    if status in ['confirmed', 'cancelled', 'completed']:
        reservation.status = status
        db.session.commit()
        flash('Rezervasyon durumu güncellendi.', 'success')
    
    return redirect(url_for('admin.reservation_detail', reservation_id=reservation.id))

@admin.route('/users')
@login_required
@admin_required
def users():
    """Kullanıcı yönetimi"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    
    query = User.query
    if search:
        query = query.filter(
            (User.email.ilike(f'%{search}%')) |
            (User.name.ilike(f'%{search}%'))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10
    )
    
    return render_template('admin/users.html', users=users, search=search)

@admin.route('/user/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """Kullanıcı detayı"""
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@admin.route('/user/<int:user_id>/status', methods=['POST'])
@login_required
@admin_required
def update_user_status(user_id):
    """Kullanıcı durumunu güncelle"""
    user = User.query.get_or_404(user_id)
    is_active = request.form.get('is_active') == 'true'
    
    user.is_active = is_active
    db.session.commit()
    
    return jsonify({'success': True})

@admin.route('/maintenance')
@login_required
@admin_required
def maintenance():
    """Bakım yönetimi"""
    page = request.args.get('page', 1, type=int)
    
    # İstatistikler
    pending_count = MaintenanceRecord.query.filter_by(status='pending').count()
    completed_count = MaintenanceRecord.query.filter_by(status='completed').count()
    total_cost = db.session.query(func.sum(MaintenanceRecord.cost)).filter(
        MaintenanceRecord.status == 'completed'
    ).scalar() or 0
    
    # Bakım kayıtları
    maintenances = MaintenanceRecord.query.order_by(
        MaintenanceRecord.created_at.desc()
    ).paginate(page=page, per_page=10)
    
    # Odalar
    rooms = Room.query.all()
    
    return render_template('admin/maintenance.html',
                         maintenances=maintenances,
                         pending_count=pending_count,
                         completed_count=completed_count,
                         total_cost=total_cost,
                         rooms=rooms)

@admin.route('/maintenance/add', methods=['POST'])
@login_required
@admin_required
def add_maintenance():
    """Yeni bakım kaydı ekle"""
    data = request.get_json()
    
    maintenance = MaintenanceRecord(
        room_id=data['room_id'],
        type=data['type'],
        description=data['description'],
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
        estimated_cost=float(data['estimated_cost']) if data['estimated_cost'] else None
    )
    
    db.session.add(maintenance)
    db.session.commit()
    
    return jsonify({'success': True})

@admin.route('/maintenance/<int:maintenance_id>/complete', methods=['POST'])
@login_required
@admin_required
def complete_maintenance(maintenance_id):
    """Bakım kaydını tamamla"""
    maintenance = MaintenanceRecord.query.get_or_404(maintenance_id)
    maintenance.status = 'completed'
    maintenance.end_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True})

@admin.route('/reports')
@login_required
@admin_required
def reports():
    """Raporlar"""
    # Son 30 günlük istatistikler
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Toplam gelir
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'completed',
        Payment.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Doluluk oranı
    total_rooms = Room.query.count()
    occupied_rooms = Reservation.query.filter(
        Reservation.status == 'confirmed',
        Reservation.check_in <= datetime.utcnow(),
        Reservation.check_out >= datetime.utcnow()
    ).count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Ortalama kalış süresi
    avg_stay = db.session.query(
        func.avg(Reservation.check_out - Reservation.check_in)
    ).filter(
        Reservation.status == 'completed',
        Reservation.check_out >= thirty_days_ago
    ).scalar()
    avg_stay_duration = round(avg_stay.days) if avg_stay else 0
    
    # Gelir grafiği verileri
    revenue_data = db.session.query(
        func.date(Payment.created_at).label('date'),
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.status == 'completed',
        Payment.created_at >= thirty_days_ago
    ).group_by(
        func.date(Payment.created_at)
    ).all()
    
    revenue_dates = [str(r.date) for r in revenue_data]
    revenue_amounts = [float(r.total) for r in revenue_data]
    
    # Doluluk oranı grafiği verileri
    occupancy_data = []
    current_date = thirty_days_ago
    while current_date <= datetime.utcnow():
        occupied = Reservation.query.filter(
            Reservation.status == 'confirmed',
            Reservation.check_in <= current_date,
            Reservation.check_out >= current_date
        ).count()
        occupancy_data.append({
            'date': str(current_date.date()),
            'rate': (occupied / total_rooms * 100) if total_rooms > 0 else 0
        })
        current_date += timedelta(days=1)
    
    occupancy_dates = [d['date'] for d in occupancy_data]
    occupancy_rates = [d['rate'] for d in occupancy_data]
    
    # Oda tiplerine göre gelir dağılımı
    room_type_revenue = db.session.query(
        Room.room_type,
        func.sum(Payment.amount).label('total')
    ).join(
        Reservation, Reservation.room_id == Room.id
    ).join(
        Payment, Payment.reservation_id == Reservation.id
    ).filter(
        Payment.status == 'completed',
        Payment.created_at >= thirty_days_ago
    ).group_by(Room.room_type).all()
    
    room_types = [r[0] for r in room_type_revenue]
    room_type_amounts = [float(r[1]) for r in room_type_revenue]
    
    # En çok tercih edilen odalar
    popular_rooms = db.session.query(
        Room,
        func.count(Reservation.id).label('total_bookings'),
        func.sum(Payment.amount).label('total_revenue'),
        func.avg(Room.rating).label('avg_rating')
    ).join(
        Reservation, Reservation.room_id == Room.id
    ).join(
        Payment, Payment.reservation_id == Reservation.id
    ).filter(
        Payment.status == 'completed',
        Payment.created_at >= thirty_days_ago
    ).group_by(Room).order_by(
        func.count(Reservation.id).desc()
    ).limit(5).all()
    
    return render_template('admin/reports.html',
                         total_revenue=total_revenue,
                         occupancy_rate=occupancy_rate,
                         avg_stay_duration=avg_stay_duration,
                         revenue_dates=revenue_dates,
                         revenue_data=revenue_amounts,
                         occupancy_dates=occupancy_dates,
                         occupancy_data=occupancy_rates,
                         room_types=room_types,
                         room_type_revenue=room_type_amounts,
                         popular_rooms=popular_rooms) 