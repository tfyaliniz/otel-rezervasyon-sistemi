import os

class Config:
    SECRET_KEY = 'BURAYA_GIZLI_ANAHTARINIZI_EKLEYIN'  # Örn: os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hotel.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail ayarları
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'BURAYA_EMAIL_ADRESINIZI_EKLEYIN'  # Örn: os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = 'BURAYA_EMAIL_SIFRENIZI_EKLEYIN'  # Örn: os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'BURAYA_EMAIL_ADRESINIZI_EKLEYIN'
    
    # Google reCAPTCHA ayarları
    RECAPTCHA_PUBLIC_KEY = 'BURAYA_RECAPTCHA_SITE_KEY_EKLEYIN'  # Site key buraya gelecek
    RECAPTCHA_PRIVATE_KEY = 'BURAYA_RECAPTCHA_SECRET_KEY_EKLEYIN'  # Secret key buraya gelecek 