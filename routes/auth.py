from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from database import db
from flask_mail import Mail, Message
from flask_recaptcha import ReCaptcha

auth = Blueprint('auth', __name__)
mail = Mail()
recaptcha = ReCaptcha()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Lütfen email ve şifrenizi kontrol edin.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.email_verified and user.email != 'admin':
            flash('Lütfen önce email adresinizi doğrulayın.', 'warning')
            return redirect(url_for('auth.verify_email'))
        
        login_user(user, remember=remember)
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        if not recaptcha.verify():
            flash('Lütfen robot olmadığınızı doğrulayın.', 'danger')
            return redirect(url_for('auth.register'))
        
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            flash('Bu email adresi zaten kayıtlı.', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Doğrulama kodu oluştur ve gönder
        code = new_user.generate_verification_code()
        msg = Message('Email Doğrulama',
                     recipients=[new_user.email])
        msg.body = f'''Merhaba {new_user.name},

Email adresinizi doğrulamak için aşağıdaki kodu kullanın:

{code}

Bu kod 30 dakika süreyle geçerlidir.

İyi günler dileriz.
'''
        mail.send(msg)
        
        flash('Başarıyla kayıt oldunuz! Lütfen email adresinizi doğrulayın.', 'success')
        return redirect(url_for('auth.verify_email'))
    
    return render_template('auth/register.html')

@auth.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email adresi bulunamadı.', 'danger')
            return redirect(url_for('auth.verify_email'))
        
        if user.verify_email(code):
            flash('Email adresiniz başarıyla doğrulandı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Geçersiz veya süresi dolmuş doğrulama kodu.', 'danger')
    
    return render_template('auth/verify_email.html')

@auth.route('/resend-verification', methods=['POST'])
def resend_verification():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('Email adresi bulunamadı.', 'danger')
        return redirect(url_for('auth.verify_email'))
    
    if user.email_verified:
        flash('Bu email adresi zaten doğrulanmış.', 'info')
        return redirect(url_for('auth.login'))
    
    # Yeni doğrulama kodu oluştur ve gönder
    code = user.generate_verification_code()
    msg = Message('Email Doğrulama',
                 recipients=[user.email])
    msg.body = f'''Merhaba {user.name},

Email adresinizi doğrulamak için aşağıdaki kodu kullanın:

{code}

Bu kod 30 dakika süreyle geçerlidir.

İyi günler dileriz.
'''
    mail.send(msg)
    
    flash('Yeni doğrulama kodu email adresinize gönderildi.', 'success')
    return redirect(url_for('auth.verify_email'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('main.index')) 