from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.room import Room
from models.reservation import Reservation, Review
from models.notification import Notification
from services.room_service import RoomService
from services.reservation_service import ReservationService
from datetime import datetime
from database import db

main = Blueprint('main', __name__)
room_service = RoomService()
reservation_service = ReservationService()

@main.route('/')
def index():
    """Ana sayfa"""
    featured_rooms = room_service.get_featured_rooms()
    return render_template('main/index.html', featured_rooms=featured_rooms)

@main.route('/rooms')
def rooms():
    """Tüm odaları listele"""
    room_type = request.args.get('type')
    capacity = request.args.get('capacity', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    rooms = room_service.search_rooms(
        room_type=room_type,
        capacity=capacity,
        min_price=min_price,
        max_price=max_price
    )
    
    return render_template('main/rooms.html', rooms=rooms)

@main.route('/room/<int:room_id>')
def room_detail(room_id):
    """Oda detayları"""
    room = room_service.get_room_by_id(room_id)
    if not room:
        flash('Oda bulunamadı.', 'error')
        return redirect(url_for('main.rooms'))
    
    reviews = Review.query.filter_by(room_id=room_id).order_by(Review.created_at.desc()).limit(5).all()
    return render_template('main/room_detail.html', room=room, reviews=reviews)

@main.route('/room/<int:room_id>/reviews')
def room_reviews(room_id):
    """Oda değerlendirmeleri"""
    room = room_service.get_room_by_id(room_id)
    if not room:
        flash('Oda bulunamadı.', 'error')
        return redirect(url_for('main.rooms'))
    
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(room_id=room_id).order_by(Review.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('main/room_reviews.html', room=room, reviews=reviews)

@main.route('/room/<int:room_id>/reserve', methods=['GET', 'POST'])
@login_required
def reserve_room(room_id):
    """Oda rezervasyonu"""
    room = room_service.get_room_by_id(room_id)
    if not room:
        flash('Oda bulunamadı.', 'error')
        return redirect(url_for('main.rooms'))
    
    if request.method == 'POST':
        check_in = datetime.strptime(request.form['check_in'], '%Y-%m-%d')
        check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d')
        guests = int(request.form['guests'])
        special_requests = request.form.get('special_requests')
        
        try:
            reservation = reservation_service.create_reservation(
                user_id=current_user.id,
                room_id=room_id,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                special_requests=special_requests
            )
            flash('Rezervasyonunuz başarıyla oluşturuldu.', 'success')
            return redirect(url_for('main.reservation_detail', reservation_id=reservation.id))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('main/reserve_room.html', room=room)

@main.route('/reservations')
@login_required
def my_reservations():
    """Kullanıcının rezervasyonları"""
    status = request.args.get('status')
    reservations = reservation_service.get_user_reservations(current_user.id, status)
    return render_template('main/my_reservations.html', reservations=reservations)

@main.route('/reservation/<int:reservation_id>')
@login_required
def reservation_detail(reservation_id):
    """Rezervasyon detayları"""
    reservation = reservation_service.get_reservation_by_id(reservation_id)
    if not reservation or (reservation.user_id != current_user.id and not current_user.is_admin):
        flash('Rezervasyon bulunamadı.', 'error')
        return redirect(url_for('main.my_reservations'))
    
    return render_template('main/reservation_detail.html', reservation=reservation)

@main.route('/notifications')
@login_required
def notifications():
    """Kullanıcı bildirimleri"""
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.is_read.asc(),
        Notification.created_at.desc()
    ).paginate(page=page, per_page=10)
    
    # Okunmamış bildirimleri okundu olarak işaretle
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notification in unread_notifications:
        notification.is_read = True
    db.session.commit()
    
    return render_template('main/notifications.html', notifications=notifications)

@main.route('/profile')
@login_required
def profile():
    """Kullanıcı profili"""
    return render_template('main/profile.html')

@main.route('/reservation/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.filter_by(
        id=reservation_id,
        user_id=current_user.id
    ).first_or_404()
    
    if reservation.status not in ['pending', 'confirmed']:
        flash('Bu rezervasyon iptal edilemez.', 'danger')
        return redirect(url_for('main.my_reservations'))
    
    reservation.status = 'cancelled'
    db.session.commit()
    
    flash('Rezervasyonunuz iptal edildi.', 'success')
    return redirect(url_for('main.my_reservations')) 