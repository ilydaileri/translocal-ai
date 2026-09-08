from flask import Blueprint, jsonify, render_template, request
from app.services.ai_service import yapay_zeka_servisi, YapayZekaServisHatasi, ai_service, AIServiceError

# Veritabanı fonksiyonlarını hem hocanın hem arkadaşının isimlendirmesine uyumlu içe aktarıyoruz
try:
    from app.database import musteri_adayi_ekle, tum_adaylari_getir
except ImportError:
    from app.database import lead_ekle as musteri_adayi_ekle, tum_leadler as tum_adaylari_getir

# Blueprint tanımları (Hem hocanın api_arayuzu/sayfa_arayuzu hem api_bp/web_bp adlandırmasıyla uyumlu)
api_bp = Blueprint("api", __name__)
web_bp = Blueprint("sayfalar", __name__)

# Alias'lar
api_arayuzu = api_bp
sayfa_arayuzu = web_bp


# ─── SAYFALAR (Arayüzler) ─────────────────────────────

@web_bp.route("/", methods=["GET"])
def ana_sayfa():
    """Son kullanıcıya gösterilen ana web sayfası."""
    return render_template("index.html")


@web_bp.route("/panel", methods=["GET"])
@web_bp.route("/dashboard", methods=["GET"])
def yonetim_paneli():
    """Müşteri adaylarının listelendiği yönetim paneli sayfası."""
    return render_template("dashboard.html")


# ─── API UÇ NOKTALARI (Endpoints) ──────────────────────

@api_bp.route("/sohbet", methods=["POST"])
def sohbet_et():
    """Kullanıcı mesajını alıp yapay zeka servisine iletir ve yanıt döner."""
    veri = request.get_json(silent=True) or {}
    mesaj = veri.get("mesaj")
    gecmis = veri.get("gecmis", [])

    if not mesaj or not str(mesaj).strip():
        return jsonify({"basari": False, "hata": "Mesaj alanı boş bırakılamaz."}), 400

    try:
        yanit = yapay_zeka_servisi.yanit_uret(str(mesaj).strip(), gecmis)
        return jsonify({"basari": True, "cevap": yanit}), 200
    except (YapayZekaServisHatasi, AIServiceError) as e:
        return jsonify({"basari": False, "hata": f"Yapay zeka servisine ulaşılamadı: {str(e)}"}), 503


@api_bp.route("/adaylar", methods=["POST"])
@api_bp.route("/leads", methods=["POST"])
def aday_kaydet():
    """İletişim formundan gelen müşteri adayı bilgilerini kaydeder."""
    veri = request.get_json(silent=True) or {}
    isim = veri.get("isim")
    telefon = veri.get("telefon")
    mesaj = veri.get("mesaj", "")

    if not isim or not str(isim).strip():
        return jsonify({"basari": False, "hata": "İsim bilgisi zorunludur."}), 400

    if not telefon or not str(telefon).strip():
        return jsonify({"basari": False, "hata": "Telefon bilgisi zorunludur."}), 400

    musteri_adayi_ekle(str(isim).strip(), str(telefon).strip(), str(mesaj).strip() if mesaj else None)
    return jsonify({"basari": True, "mesaj": "Bilgileriniz başarıyla sistemimize kaydedildi."}), 201


@api_bp.route("/adaylar", methods=["GET"])
@api_bp.route("/leads", methods=["GET"])
def adaylari_listele():
    """Dashboard tablosu için tüm müşteri adaylarını listeler."""
    adaylar = tum_adaylari_getir() or []
    
    # Liste dict veya SQLite Row objesi gelse de güvenli formata çevirme
    sonuc = []
    for item in adaylar:
        if isinstance(item, dict):
            sonuc.append(item)
        else:
            sonuc.append({
                "id": item[0] if len(item) > 0 else None,
                "isim": item[1] if len(item) > 1 else "",
                "telefon": item[2] if len(item) > 2 else "",
                "mesaj": item[3] if len(item) > 3 else "",
                "tarih": item[4] if len(item) > 4 else ""
            })

    return jsonify({
        "basari": True,
        "toplam": len(sonuc),
        "adaylar": sonuc,
        "leadler": sonuc
    }), 200