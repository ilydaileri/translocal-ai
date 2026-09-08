import os
from flask import Flask, jsonify
from flask_cors import CORS

import config
from app.database import veritabani_baslat
from app.routes import web_bp, api_bp


def create_app(config_class=None):
    app = Flask(__name__)

    # 1. Konfigürasyonu Yükle
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(config)

    # Yedek doğrudan atamalar (garanti olsun diye)
    app.config.setdefault("BUSINESS_CONTEXT", getattr(config, "BUSINESS_CONTEXT", "Sen yardımcı bir iş asistanısın."))
    app.config.setdefault("GROQ_API_KEY", getattr(config, "GROQ_API_KEY", ""))
    app.config.setdefault("GEMINI_API_KEY", getattr(config, "GEMINI_API_KEY", ""))
    app.config.setdefault("OPENAI_API_KEY", getattr(config, "OPENAI_API_KEY", ""))
    app.config.setdefault("AI_PROVIDER", getattr(config, "AI_PROVIDER", "groq"))
    app.config.setdefault("DATABASE_URL", getattr(config, "DATABASE_URL", "smartlead.db"))

    # 2. CORS Yapılandırması (Hem Wix canlı sitesi hem yerel testler için)
    CORS(app, resources={
        r"/*": {
            "origins": [
                "https://ilaydaileri.wixsite.com",
                r"https://.*\.wixsite\.com",
                r"https://.*\.wixstudio\.io",
                "http://localhost:5000",
                "http://127.0.0.1:5000"
            ]
        }
    })

    # 3. Veritabanını Başlat
    veritabani_baslat(app)

    # 4. Blueprint'leri Kaydet
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # 5. Sunucu Canlılık Kontrolü (Health Check)
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "basari": True,
            "status": "ok"
        }), 200

    return app


# Hocanın Türkçe fonksiyon adı kullanımı için alias
uygulama_olustur = create_app