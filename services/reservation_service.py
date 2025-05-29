from flask import current_app
from flask_mail import Message
from models.reservation import Reservation, Payment
from models.room import Room
from models.user import User
from models.notification import Notification
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

class ReservationService:
    def create_reservation(self, user_id, room_id, check_in, check_out, guests, special_requests=None):
        """Yeni rezervasyon oluştur"""
        # Oda kontrolü
        room = Room.query.get_or_404(room_id)
        if not room.is_active:
            raise ValueError('Bu oda şu anda rezervasyona kapalı.')
        
        # Tarih kontrolü
        if check_in >= check_out:
            raise ValueError('Çıkış tarihi giriş tarihinden sonra olmalıdır.')
        
        if check_in < datetime.now().date():
            raise ValueError('Geçmiş tarihli rezervasyon yapılamaz.')
        
        # Kapasite kontrolü
        if guests > room.capacity:
            raise ValueError(f'Bu oda en fazla {room.capacity} kişi kapasitelidir.')
        
        # Müsaitlik kontrolü
        if not room.is_available_for_dates(check_in, check_out):
            raise ValueError('Seçilen tarihler için oda müsait değil.')
        
        # Toplam fiyat hesaplama
        total_nights = (check_out - check_in).days
        total_price = room.price * total_nights
        
        # Rezervasyon oluştur
        reservation = Reservation(
            user_id=user_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            special_requests=special_requests,
            total_price=total_price,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        # Bildirim gönder
        self._send_reservation_notification(reservation)
        
        return reservation
    
    def update_reservation_status(self, reservation_id, status):
        """Rezervasyon durumunu güncelle"""
        reservation = Reservation.query.get_or_404(reservation_id)
        
        if status not in ['pending', 'confirmed', 'cancelled', 'completed']:
            raise ValueError('Geçersiz rezervasyon durumu.')
        
        reservation.status = status
        reservation.updated_at = datetime.utcnow()
        
        if status == 'confirmed':
            reservation.confirmed_at = datetime.utcnow()
        elif status == 'cancelled':
            reservation.cancelled_at = datetime.utcnow()
        elif status == 'completed':
            reservation.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Bildirim gönder
        self._send_status_notification(reservation)
        
        return reservation
    
    def cancel_reservation(self, reservation_id, user_id):
        """Rezervasyon iptal et"""
        reservation = Reservation.query.get_or_404(reservation_id)
        
        # Yetki kontrolü
        if reservation.user_id != user_id and not User.query.get(user_id).is_admin:
            raise ValueError('Bu işlem için yetkiniz yok.')
        
        # İptal edilebilirlik kontrolü
        if reservation.status not in ['pending', 'confirmed']:
            raise ValueError('Bu rezervasyon iptal edilemez.')
        
        if reservation.check_in <= datetime.now().date():
            raise ValueError('Başlamış veya geçmiş rezervasyonlar iptal edilemez.')
        
        reservation.status = 'cancelled'
        reservation.cancelled_at = datetime.utcnow()
        db.session.commit()
        
        # Bildirim gönder
        self._send_cancellation_notification(reservation)
        
        return reservation
    
    def create_payment(self, reservation_id, amount, payment_method):
        """Ödeme oluştur"""
        reservation = Reservation.query.get_or_404(reservation_id)
        
        if reservation.status != 'confirmed':
            raise ValueError('Sadece onaylanmış rezervasyonlar için ödeme yapılabilir.')
        
        payment = Payment(
            reservation_id=reservation_id,
            amount=amount,
            payment_method=payment_method,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return payment
    
    def update_payment_status(self, payment_id, status):
        """Ödeme durumunu güncelle"""
        payment = Payment.query.get_or_404(payment_id)
        
        if status not in ['pending', 'completed', 'failed', 'refunded']:
            raise ValueError('Geçersiz ödeme durumu.')
        
        payment.status = status
        payment.updated_at = datetime.utcnow()
        
        if status == 'completed':
            payment.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Bildirim gönder
        self._send_payment_notification(payment)
        
        return payment
    
    def get_reservation_by_id(self, reservation_id):
        """ID ile rezervasyon getir"""
        return Reservation.query.get_or_404(reservation_id)
    
    def get_user_reservations(self, user_id, status=None):
        """Kullanıcının rezervasyonlarını getir"""
        query = Reservation.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Reservation.created_at.desc()).all()
    
    def get_all_reservations(self, status=None, page=1, per_page=20):
        """Tüm rezervasyonları getir"""
        query = Reservation.query
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Reservation.created_at.desc()).paginate(page=page, per_page=per_page)
    
    def get_upcoming_checkouts(self, days=1):
        """Yaklaşan çıkışları getir"""
        target_date = datetime.now().date() + timedelta(days=days)
        return Reservation.query.filter(
            Reservation.status == 'confirmed',
            Reservation.check_out == target_date
        ).all()
    
    def get_upcoming_checkins(self, days=1):
        """Yaklaşan girişleri getir"""
        target_date = datetime.now().date() + timedelta(days=days)
        return Reservation.query.filter(
            Reservation.status == 'confirmed',
            Reservation.check_in == target_date
        ).all()
    
    def _send_reservation_notification(self, reservation):
        """Rezervasyon bildirimi gönder"""
        # Sistem bildirimi
        notification = Notification(
            user_id=reservation.user_id,
            title='Yeni Rezervasyon',
            message=f'Rezervasyonunuz başarıyla oluşturuldu. Rezervasyon numaranız: {reservation.id}',
            type='reservation',
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        
        # E-posta bildirimi
        msg = Message(
            'Rezervasyon Onayı',
            recipients=[reservation.user.email]
        )
        msg.body = f'''Sayın {reservation.user.name},

Rezervasyonunuz başarıyla oluşturuldu.

Rezervasyon Detayları:
- Rezervasyon No: {reservation.id}
- Oda: {reservation.room.room_type} - {reservation.room.room_number}
- Giriş Tarihi: {reservation.check_in.strftime('%d/%m/%Y')}
- Çıkış Tarihi: {reservation.check_out.strftime('%d/%m/%Y')}
- Kişi Sayısı: {reservation.guests}
- Toplam Fiyat: ₺{reservation.total_price:,.2f}

Rezervasyonunuz şu anda onay bekliyor. Onaylandığında size bilgi verilecektir.

İyi günler dileriz.
'''
        mail.send(msg)
        db.session.commit()
    
    def _send_status_notification(self, reservation):
        """Durum değişikliği bildirimi gönder"""
        status_messages = {
            'confirmed': 'onaylandı',
            'cancelled': 'iptal edildi',
            'completed': 'tamamlandı'
        }
        
        if reservation.status in status_messages:
            # Sistem bildirimi
            notification = Notification(
                user_id=reservation.user_id,
                title='Rezervasyon Durumu',
                message=f'Rezervasyonunuz {status_messages[reservation.status]}.',
                type='reservation',
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            
            # E-posta bildirimi
            msg = Message(
                'Rezervasyon Durumu Güncellendi',
                recipients=[reservation.user.email]
            )
            msg.body = f'''Sayın {reservation.user.name},

Rezervasyonunuzun durumu güncellendi.

Rezervasyon Detayları:
- Rezervasyon No: {reservation.id}
- Oda: {reservation.room.room_type} - {reservation.room.room_number}
- Durum: {status_messages[reservation.status].title()}

İyi günler dileriz.
'''
            mail.send(msg)
            db.session.commit()
    
    def _send_cancellation_notification(self, reservation):
        """İptal bildirimi gönder"""
        # Sistem bildirimi
        notification = Notification(
            user_id=reservation.user_id,
            title='Rezervasyon İptali',
            message=f'Rezervasyonunuz iptal edildi.',
            type='reservation',
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        
        # E-posta bildirimi
        msg = Message(
            'Rezervasyon İptali',
            recipients=[reservation.user.email]
        )
        msg.body = f'''Sayın {reservation.user.name},

Rezervasyonunuz iptal edildi.

Rezervasyon Detayları:
- Rezervasyon No: {reservation.id}
- Oda: {reservation.room.room_type} - {reservation.room.room_number}
- İptal Tarihi: {datetime.now().strftime('%d/%m/%Y')}

İyi günler dileriz.
'''
        mail.send(msg)
        db.session.commit()
    
    def _send_payment_notification(self, payment):
        """Ödeme bildirimi gönder"""
        status_messages = {
            'completed': 'tamamlandı',
            'failed': 'başarısız oldu',
            'refunded': 'iade edildi'
        }
        
        if payment.status in status_messages:
            # Sistem bildirimi
            notification = Notification(
                user_id=payment.reservation.user_id,
                title='Ödeme Durumu',
                message=f'Ödemeniz {status_messages[payment.status]}.',
                type='payment',
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
            
            # E-posta bildirimi
            msg = Message(
                'Ödeme Durumu',
                recipients=[payment.reservation.user.email]
            )
            msg.body = f'''Sayın {payment.reservation.user.name},

Ödemenizin durumu güncellendi.

Ödeme Detayları:
- Rezervasyon No: {payment.reservation_id}
- Tutar: ₺{payment.amount:,.2f}
- Durum: {status_messages[payment.status].title()}

İyi günler dileriz.
'''
            mail.send(msg)
            db.session.commit() 