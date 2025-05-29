from datetime import datetime
import uuid
import requests
from app import db
from models.reservation import Payment, Reservation
from services.notification_service import NotificationService

class PaymentService:
    def __init__(self):
        self.notification_service = NotificationService()

    def process_payment(self, reservation_id, payment_method, card_info=None):
        """Ödeme işlemini gerçekleştirir"""
        reservation = Reservation.query.get_or_404(reservation_id)
        
        if reservation.payment_status != 'Bekliyor':
            raise ValueError("Bu rezervasyon için ödeme yapılamaz")
        
        # Ödeme kaydı oluştur
        payment = Payment(
            reservation_id=reservation_id,
            amount=reservation.total_price,
            payment_method=payment_method,
            transaction_id=str(uuid.uuid4())
        )
        
        try:
            # Ödeme işlemini gerçekleştir
            if payment_method == 'credit_card':
                self._process_credit_card_payment(payment, card_info)
            elif payment_method == 'bank_transfer':
                self._process_bank_transfer(payment)
            else:
                raise ValueError("Geçersiz ödeme yöntemi")
            
            # Ödeme başarılı
            payment.status = 'Tamamlandı'
            reservation.payment_status = 'Tamamlandı'
            
            db.session.add(payment)
            db.session.commit()
            
            # Bildirim gönder
            self._send_payment_notifications(payment, 'success')
            
            return payment
            
        except Exception as e:
            # Ödeme başarısız
            payment.status = 'Başarısız'
            db.session.add(payment)
            db.session.commit()
            
            # Bildirim gönder
            self._send_payment_notifications(payment, 'failed')
            
            raise e

    def get_payment_history(self, reservation_id):
        """Rezervasyonun ödeme geçmişini getirir"""
        return Payment.query.filter_by(reservation_id=reservation_id)\
            .order_by(Payment.created_at.desc()).all()

    def get_payment_status(self, payment_id):
        """Ödeme durumunu kontrol eder"""
        payment = Payment.query.get_or_404(payment_id)
        return payment.status

    def _process_credit_card_payment(self, payment, card_info):
        """Kredi kartı ödemesini işler"""
        # Burada gerçek bir ödeme API'si entegrasyonu yapılacak
        # Örnek olarak sahte bir API çağrısı:
        response = requests.post(
            'https://api.odeme.com/process',
            json={
                'amount': payment.amount,
                'currency': 'TRY',
                'card_number': card_info['number'],
                'expiry_month': card_info['expiry_month'],
                'expiry_year': card_info['expiry_year'],
                'cvv': card_info['cvv'],
                'transaction_id': payment.transaction_id
            }
        )
        
        if response.status_code != 200:
            raise Exception("Ödeme işlemi başarısız")

    def _process_bank_transfer(self, payment):
        """Banka havalesi işlemini hazırlar"""
        # Havale bilgilerini hazırla
        payment.status = 'Bekliyor'
        return {
            'bank_name': 'Örnek Bank',
            'account_name': 'Otel Rezervasyon',
            'iban': 'TR123456789012345678901234',
            'amount': payment.amount,
            'reference': payment.transaction_id
        }

    def _send_payment_notifications(self, payment, status):
        """Ödeme bildirimleri gönderir"""
        reservation = payment.reservation
        user_id = reservation.user_id
        
        if status == 'success':
            # Sistem bildirimi
            self.notification_service.send_system_notification(
                user_id=user_id,
                title='Ödeme Başarılı',
                message=f'Rezervasyon ödemesi başarıyla tamamlandı. İşlem No: {payment.transaction_id}'
            )
            
            # E-posta bildirimi
            self.notification_service.send_email(
                user_id=user_id,
                subject='Ödeme Onayı',
                template='email/payment_success.html',
                payment=payment,
                reservation=reservation
            )
            
        else:
            # Sistem bildirimi
            self.notification_service.send_system_notification(
                user_id=user_id,
                title='Ödeme Başarısız',
                message=f'Rezervasyon ödemesi başarısız oldu. Lütfen tekrar deneyin.'
            )
            
            # E-posta bildirimi
            self.notification_service.send_email(
                user_id=user_id,
                subject='Ödeme Başarısız',
                template='email/payment_failed.html',
                payment=payment,
                reservation=reservation
            ) 