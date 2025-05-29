// Form doğrulama
function validateForm() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');

    if (password && confirmPassword) {
        if (password.value !== confirmPassword.value) {
            alert('Şifreler eşleşmiyor!');
            return false;
        }
    }

    return true;
}

// Tarih kontrolü
function setupDateInputs() {
    const checkIn = document.getElementById('check_in');
    const checkOut = document.getElementById('check_out');

    if (checkIn && checkOut) {
        const today = new Date().toISOString().split('T')[0];
        checkIn.min = today;
        checkOut.min = today;

        checkIn.addEventListener('change', function() {
            checkOut.min = this.value;
            if (checkOut.value && checkOut.value < this.value) {
                checkOut.value = this.value;
            }
        });
    }
}

// Rezervasyon iptal onayı
function confirmCancel(event) {
    if (!confirm('Bu rezervasyonu iptal etmek istediğinizden emin misiniz?')) {
        event.preventDefault();
    }
}

// Sayfa yüklendiğinde çalışacak fonksiyonlar
document.addEventListener('DOMContentLoaded', function() {
    setupDateInputs();

    // Form doğrulama
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm()) {
                event.preventDefault();
            }
        });
    });

    // İptal butonları için onay
    const cancelButtons = document.querySelectorAll('.cancel-reservation');
    cancelButtons.forEach(button => {
        button.addEventListener('click', confirmCancel);
    });

    // Alert mesajlarını otomatik gizle
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 3000);
    });
}); 