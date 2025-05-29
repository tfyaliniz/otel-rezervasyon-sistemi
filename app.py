from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_recaptcha import ReCaptcha
from database import db
from models.user import User
from werkzeug.security import generate_password_hash
from markupsafe import Markup
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Veritabanı
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Login yönetimi
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Mail
    mail = Mail(app)
    
    # reCAPTCHA
    recaptcha = ReCaptcha()
    recaptcha.init_app(app)
    
    # Blueprint'ler
    from routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    # Admin hesabını oluştur
    with app.app_context():
        db.create_all()
        
        # Admin hesabı yoksa oluştur
        admin_user = User.query.filter_by(email='admin').first()
        if not admin_user:
            admin_user = User(
                email='admin',
                name='Admin',
                password_hash=generate_password_hash('admin'),
                is_admin=True,
                email_verified=True
            )
            db.session.add(admin_user)
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 