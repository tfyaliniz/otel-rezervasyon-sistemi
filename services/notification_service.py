from flask import current_app
from flask_mail import Message
from models.notification import Notification
from datetime import datetime
import requests
import json

class NotificationService:
    def create_notification(self, user_id, title, message, type='system'):
        """Yeni bildirim oluştur"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification
    
    def mark_as_read(self, notification_id):
        """Bildirimi okundu olarak işaretle"""
        notification = Notification.query.get_or_404(notification_id)
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        return notification
    
    def mark_all_as_read(self, user_id):
        """Tüm bildirimleri okundu olarak işaretle"""
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        db.session.commit()
    
    def delete_notification(self, notification_id):
        """Bildirimi sil"""
        notification = Notification.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
    
    def get_user_notifications(self, user_id, page=1, per_page=20):
        """Kullanıcının bildirimlerini getir"""
        return Notification.query.filter_by(user_id=user_id).order_by(
            Notification.is_read.asc(),
            Notification.created_at.desc()
        ).paginate(page=page, per_page=per_page)
    
    def get_unread_count(self, user_id):
        """Okunmamış bildirim sayısını getir"""
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    
    def send_email(self, recipients, subject, body):
        """E-posta gönder"""
        msg = Message(
            subject,
            recipients=recipients,
            body=body
        )
        mail.send(msg)
    
    def send_sms(self, phone_number, message):
        """SMS gönder"""
        if not current_app.config.get('SMS_API_KEY'):
            raise ValueError('SMS API anahtarı yapılandırılmamış.')
        
        url = current_app.config['SMS_API_URL']
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {current_app.config['SMS_API_KEY']}"
        }
        
        data = {
            'phone': phone_number,
            'message': message,
            'sender_id': current_app.config['SMS_SENDER_ID']
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'SMS gönderimi başarısız: {str(e)}')
            raise ValueError('SMS gönderilemedi. Lütfen daha sonra tekrar deneyin.') 