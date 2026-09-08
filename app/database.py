import sqlite3
from flask import current_app, g

DATABASE_DEFAULT = "smartlead.db"


def baglanti_al():
    """Flask app context ve config ile uyumlu veritabanı bağlantısı sağlar."""
    vt_yolu = current_app.config.get("DATABASE_URL", DATABASE_DEFAULT) if current_app else DATABASE_DEFAULT
    if "db" not in g:
        g.db = sqlite3.connect(vt_yolu)
        g.db.row_factory = sqlite3.Row
    return g.db


# Alias
get_db = baglanti_al


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def veritabani_baslat(uygulama):
    """Tabloyu oluşturur ve uygulama bağlamı kapanırken bağlantıyı temizler."""
    with uygulama.app_context():
        db = baglanti_al()
        # Hem 'musteri_adaylari' hem de 'leads' yapısını tek tabloda kuruyoruz
        db.execute("""
            CREATE TABLE IF NOT EXISTS musteri_adaylari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                telefon TEXT NOT NULL,
                mesaj TEXT,
                olusturulma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Eski leads tablosu varsa veya kullanılırsa diye görünüm (VIEW) garantisi
        db.execute("""
            CREATE VIEW IF NOT EXISTS leads AS 
            SELECT id, isim, telefon, mesaj, olusturulma_tarihi AS tarih 
            FROM musteri_adaylari
        """)
        db.commit()

    uygulama.teardown_appcontext(close_db)


# Alias
init_db = veritabani_baslat


def musteri_adayi_ekle(isim: str, telefon: str, mesaj: str = None):
    db = baglanti_al()
    db.execute(
        "INSERT INTO musteri_adaylari (isim, telefon, mesaj) VALUES (?, ?, ?)",
        (isim, telefon, mesaj)
    )
    db.commit()


# Alias
lead_ekle = musteri_adayi_ekle


def tum_adaylari_getir() -> list:
    db = baglanti_al()
    satirlar = db.execute(
        "SELECT id, isim, telefon, mesaj, olusturulma_tarihi FROM musteri_adaylari ORDER BY olusturulma_tarihi DESC, id DESC"
    ).fetchall()

    adaylar = []
    for satir in satirlar:
        adaylar.append({
            "id": satir["id"],
            "isim": satir["isim"],
            "telefon": satir["telefon"],
            "mesaj": satir["mesaj"],
            "olusturulma_tarihi": satir["olusturulma_tarihi"],
            "tarih": satir["olusturulma_tarihi"]  # Arkadaşının frontend'i 'tarih' ararsa diye
        })
    return adaylar


# Alias
tum_leadler = tum_adaylari_getir