import os
from dotenv import load_dotenv

load_dotenv()


class Ayarlar:
    # Flask ve Veritabanı
    SECRET_KEY = os.environ.get("SECRET_KEY", "smartlead-gizli-anahtar-12345")
    DATABASE_URL = os.environ.get("DATABASE_URL", "smartlead.db")

    # API Anahtarları ve Tercih Edilen Sağlayıcı
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "groq")

    # SmartLead Özel Sistem Bağlamı (Prompt)
    BUSINESS_CONTEXT = os.environ.get(
        "BUSINESS_CONTEXT",
        (
            "Sen TransLocal firmasının yapay zekâ asistanısın. Küresel pazara açılmak isteyen e-ticaret şirketlerine, mobil uygulama/oyun geliştiricilerine ve profesyonellere dijital yerelleştirme (lokalizasyon), yazılım çevirisi ve uluslararası SEO hizmetleri hakkında bilgi ver. Kurumsal, inovatif ve modern bir ton kullan. Türkçe konuş.Kullanıcıyı dijital yerelleştirme hizmeti almak veya teklif/bilgi almak üzere iletişim bilgilerini (isim ve telefon) bırakmaya yönlendir."
        )
    )

    # CORS İzinleri (Wix sitesi ve yerel ortam)
    CORS_ALLOWED_ORIGINS = os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "https://ilaydaileri.wixsite.com,http://localhost:5000,http://127.0.0.1:5000"
    )


class GelistirmeAyarlari(Ayarlar):
    DEBUG = True


class UretimAyarlari(Ayarlar):
    DEBUG = False


ayar_secici = {
    "gelistirme": GelistirmeAyarlari,
    "uretim": UretimAyarlari,
    "development": GelistirmeAyarlari,
    "production": UretimAyarlari,
}

# Geriye dönük uyumluluk için modül seviyesinde doğrudan dışa aktarılan değişkenler
SECRET_KEY = Ayarlar.SECRET_KEY
DATABASE_URL = Ayarlar.DATABASE_URL
GEMINI_API_KEY = Ayarlar.GEMINI_API_KEY
GROQ_API_KEY = Ayarlar.GROQ_API_KEY
OPENAI_API_KEY = Ayarlar.OPENAI_API_KEY
AI_PROVIDER = Ayarlar.AI_PROVIDER
BUSINESS_CONTEXT = Ayarlar.BUSINESS_CONTEXT
CORS_ALLOWED_ORIGINS = Ayarlar.CORS_ALLOWED_ORIGINS

# İngilizce ve hocanın Türkçe sınıf adları için alias'lar
Config = Ayarlar
DevelopmentConfig = GelistirmeAyarlari
ProductionConfig = UretimAyarlari
config_by_name = ayar_secici