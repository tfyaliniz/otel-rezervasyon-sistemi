import subprocess
import webbrowser
import time
import os
import sys

def run_flask_app():
    # Flask uygulamasını başlat
    flask_process = subprocess.Popen([sys.executable, 'app.py'], 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    
    # Uygulamanın başlaması için biraz bekle
    time.sleep(2)
    
    # Varsayılan tarayıcıda uygulamayı aç (new=0 parametresi ile aynı sekmede aç)
    webbrowser.open('http://localhost:5000', new=0, autoraise=True)
    
    try:
        # Flask uygulaması çalışmaya devam etsin
        flask_process.wait()
    except KeyboardInterrupt:
        # Ctrl+C ile kapatıldığında düzgünce sonlandır
        flask_process.terminate()
        flask_process.wait()

if __name__ == '__main__':
    run_flask_app() 