from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from services.room_service import RoomService
from services.reservation_service import ReservationService
from services.user_service import UserService
from datetime import datetime

api = Blueprint('api', __name__)
room_service = RoomService()
reservation_service = ReservationService()
user_service = UserService()

def json_response(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return jsonify({'success': True, 'data': result})
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return decorated_function

@api.route('/rooms')
@json_response
def get_rooms():
    """Tüm odaları listeler"""
    return [room.to_dict() for room in room_service.get_all_rooms()]

@api.route('/rooms/available')
@json_response
def get_available_rooms():
    """Müsait odaları listeler"""
    check_in = datetime.strptime(request.args.get('check_in'), '%Y-%m-%d')
    check_out = datetime.strptime(request.args.get('check_out'), '%Y-%m-%d')
    capacity = request.args.get('capacity', type=int)
    room_type = request.args.get('room_type')
    
    rooms = room_service.get_available_rooms(check_in, check_out, capacity, room_type)
    return [room.to_dict() for room in rooms]

@api.route('/room/<int:room_id>')
@json_response
def get_room(room_id):
    """Oda detaylarını getirir"""
    room = room_service.get_room_by_id(room_id)
    return room.to_dict()

@api.route('/room/<int:room_id>/reviews')
@json_response
def get_room_reviews(room_id):
    """Oda değerlendirmelerini getirir"""
    room = room_service.get_room_by_id(room_id)
    return [review.to_dict() for review in room.reviews]

@api.route('/reservations', methods=['POST'])
@login_required
@json_response
def create_reservation():
    """Yeni rezervasyon oluşturur"""
    data = request.get_json()
    
    reservation = reservation_service.create_reservation(
        user_id=current_user.id,
        room_id=data['room_id'],
        check_in=datetime.strptime(data['check_in'], '%Y-%m-%d'),
        check_out=datetime.strptime(data['check_out'], '%Y-%m-%d'),
        guests=data['guests'],
        special_requests=data.get('special_requests')
    )
    
    return reservation.to_dict()

@api.route('/reservations/<int:reservation_id>')
@login_required
@json_response
def get_reservation(reservation_id):
    """Rezervasyon detaylarını getirir"""
    reservation = reservation_service.get_reservation_by_id(reservation_id)
    
    if reservation.user_id != current_user.id and not current_user.is_admin:
        raise ValueError("Bu işlem için yetkiniz yok")
        
    return reservation.to_dict()

@api.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@login_required
@json_response
def cancel_reservation(reservation_id):
    """Rezervasyonu iptal eder"""
    reservation_service.cancel_reservation(reservation_id, current_user.id)
    return {'message': 'Rezervasyon başarıyla iptal edildi'}

@api.route('/reservations/<int:reservation_id>/review', methods=['POST'])
@login_required
@json_response
def add_review(reservation_id):
    """Rezervasyon için değerlendirme ekler"""
    data = request.get_json()
    
    review = user_service.create_review(
        user_id=current_user.id,
        room_id=data['room_id'],
        reservation_id=reservation_id,
        rating=data['rating'],
        comment=data.get('comment')
    )
    
    return review.to_dict()

@api.route('/user/reservations')
@login_required
@json_response
def get_user_reservations():
    """Kullanıcının rezervasyonlarını getirir"""
    status = request.args.get('status')
    reservations = reservation_service.get_user_reservations(current_user.id, status)
    return [reservation.to_dict() for reservation in reservations]

@api.route('/room/<int:room_id>/availability')
@json_response
def check_room_availability(room_id):
    """Oda müsaitlik durumunu kontrol eder"""
    check_in = datetime.strptime(request.args.get('check_in'), '%Y-%m-%d')
    check_out = datetime.strptime(request.args.get('check_out'), '%Y-%m-%d')
    
    room = room_service.get_room_by_id(room_id)
    is_available = room.is_available_for_dates(check_in, check_out)
    
    return {
        'room_id': room_id,
        'is_available': is_available,
        'check_in': check_in.strftime('%Y-%m-%d'),
        'check_out': check_out.strftime('%Y-%m-%d')
    }

@api.route('/room/<int:room_id>/price')
@json_response
def calculate_room_price(room_id):
    """Oda fiyatını hesaplar"""
    check_in = datetime.strptime(request.args.get('check_in'), '%Y-%m-%d')
    check_out = datetime.strptime(request.args.get('check_out'), '%Y-%m-%d')
    
    room = room_service.get_room_by_id(room_id)
    total_price = room.get_price_for_dates(check_in, check_out)
    
    return {
        'room_id': room_id,
        'total_price': total_price,
        'check_in': check_in.strftime('%Y-%m-%d'),
        'check_out': check_out.strftime('%Y-%m-%d'),
        'nights': (check_out - check_in).days
    }

@api.route('/room/<int:room_id>/occupancy')
@json_response
def get_room_occupancy(room_id):
    """Oda doluluk oranını getirir"""
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
    
    occupancy_rate = room_service.get_room_occupancy_rate(room_id, start_date, end_date)
    
    return {
        'room_id': room_id,
        'occupancy_rate': occupancy_rate,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }

@api.route('/room/<int:room_id>/revenue')
@json_response
def get_room_revenue(room_id):
    """Oda gelirini getirir"""
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
    
    revenue = room_service.get_room_revenue(room_id, start_date, end_date)
    
    return {
        'room_id': room_id,
        'revenue': revenue,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    } 