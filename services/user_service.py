from flask import current_app
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.reservation import Review
from datetime import datetime, timedelta
import jwt
import os

class UserService:
    def create_user(self, name, email, password, phone=None, address=None):
        """Yeni kullanıcı oluştur"""
        if User.query.filter_by(email=email).first():
            raise ValueError('Bu e-posta adresi zaten kullanılıyor.')
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            address=address,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        return user
    
    def authenticate_user(self, email, password):
        """Kullanıcı girişi doğrula"""
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                raise ValueError('Hesabınız devre dışı bırakılmış.')
            return user
        return None
    
    def update_user(self, user_id, name=None, phone=None, address=None):
        """Kullanıcı bilgilerini güncelle"""
        user = User.query.get_or_404(user_id)
        
        if name:
            user.name = name
        if phone:
            user.phone = phone
        if address:
            user.address = address
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return user
    
    def update_password(self, user_id, password):
        """Kullanıcı şifresini güncelle"""
        user = User.query.get_or_404(user_id)
        user.password_hash = generate_password_hash(password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_avatar(self, user_id, filename):
        """Kullanıcı profil resmini güncelle"""
        user = User.query.get_or_404(user_id)
        
        # Eski resmi sil
        if user.avatar and user.avatar != 'default.jpg':
            try:
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], 'users', user.avatar))
            except:
                pass
        
        user.avatar = filename
        user.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_user_status(self, user_id, is_active):
        """Kullanıcı durumunu güncelle"""
        user = User.query.get_or_404(user_id)
        user.is_active = is_active
        user.updated_at = datetime.utcnow()
        db.session.commit()
    
    def search_users(self, search=None, page=1, per_page=20):
        """Kullanıcı ara"""
        query = User.query
        
        if search:
            search = f"%{search}%"
            query = query.filter(
                (User.name.ilike(search)) |
                (User.email.ilike(search)) |
                (User.phone.ilike(search))
            )
        
        return query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    
    def get_user_by_id(self, user_id):
        """ID ile kullanıcı getir"""
        return User.query.get_or_404(user_id)
    
    def get_user_by_email(self, email):
        """E-posta ile kullanıcı getir"""
        return User.query.filter_by(email=email).first()
    
    def create_review(self, user_id, room_id, reservation_id, rating, comment=None):
        """Değerlendirme oluştur"""
        if not 1 <= rating <= 5:
            raise ValueError('Değerlendirme puanı 1-5 arasında olmalıdır.')
        
        review = Review(
            user_id=user_id,
            room_id=room_id,
            reservation_id=reservation_id,
            rating=rating,
            comment=comment,
            created_at=datetime.utcnow()
        )
        
        db.session.add(review)
        db.session.commit()
        return review
    
    def generate_reset_token(self, user, expires_in=3600):
        """Şifre sıfırlama token'ı oluştur"""
        token = jwt.encode(
            {
                'reset_password': user.id,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token
    
    def verify_reset_token(self, token):
        """Şifre sıfırlama token'ını doğrula"""
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = data.get('reset_password')
            if user_id:
                return User.query.get(user_id)
        except:
            pass
        return None
    
    def send_reset_email(self, user, token):
        """Şifre sıfırlama e-postası gönder"""
        reset_url = url_for('auth.reset_password_token', token=token, _external=True)
        
        msg = Message(
            'Şifre Sıfırlama İsteği',
            recipients=[user.email]
        )
        msg.body = f'''Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:

{reset_url}

Bu bağlantı 1 saat sonra geçerliliğini yitirecektir.

Eğer şifre sıfırlama talebinde bulunmadıysanız, bu e-postayı dikkate almayın.
'''
        mail.send(msg) 