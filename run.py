import os
from app import create_app

# Uygulama fabrikasından yapılandırılmış Flask uygulamasını alıyoruz
app = create_app()

# Hocanın Türkçe değişken adlandırmasıyla uyumluluk için alias
uygulama = app

if __name__ == "__main__":
    # Port ortam değişkeninden veya varsayılan 5000'den alınır
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)