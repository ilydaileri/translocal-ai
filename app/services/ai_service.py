import logging
import requests
from flask import current_app

loglayici = logging.getLogger(__name__)


class YapayZekaServisHatasi(Exception):
    """Yapay zeka servis katmanında oluşan hatalar için özel istisna sınıfı."""
    pass


# Geriye dönük uyumluluk için alias
AIServiceError = YapayZekaServisHatasi


class YapayZekaServisi:
    def yanit_uret(self, kullanici_mesaji: str, sohbet_gecmisi: list = None) -> str:
        saglayici = current_app.config.get("AI_PROVIDER", "groq").lower()

        if saglayici == "openai":
            return self._openai_cagir(kullanici_mesaji, sohbet_gecmisi or [])
        elif saglayici == "gemini":
            return self._gemini_cagir(kullanici_mesaji, sohbet_gecmisi or [])
        else:
            return self._groq_cagir(kullanici_mesaji, sohbet_gecmisi or [])

    def _sistem_talimati_olustur(self) -> str:
        return current_app.config.get(
            "BUSINESS_CONTEXT",
            "Sen SmartLead asistanısın. Müşteri adayı analizi ve profesyonel iletişim konularında yardımcı olursun."
        )

    def _groq_cagir(self, kullanici_mesaji: str, gecmis: list) -> str:
        api_anahtari = current_app.config.get("GROQ_API_KEY", "")

        if not api_anahtari:
            loglayici.warning("GROQ_API_KEY ayarlanmamış! Demo modu devrede.")
            return self._demo_yaniti_ver(kullanici_mesaji)

        baglanti_adresi = "https://api.groq.com/openai/v1/chat/completions"
        
        mesajlar_dizisi = [{"role": "system", "content": self._sistem_talimati_olustur()}]
        for mesaj in gecmis:
            mesajlar_dizisi.append({
                "role": mesaj.get("role", "user"),
                "content": mesaj.get("content", "")
            })
        mesajlar_dizisi.append({"role": "user", "content": kullanici_mesaji})

        # Groq üzerinde güncel ve aktif üretim modeli
        gonderilecek_veri = {
            "model": "openai/gpt-oss-20b",
            "messages": mesajlar_dizisi,
            "max_tokens": 500,
            "temperature": 0.7,
        }

        try:
            sunucu_cevabi = requests.post(
                baglanti_adresi,
                json=gonderilecek_veri,
                timeout=20,
                headers={
                    "Authorization": f"Bearer {api_anahtari}",
                    "Content-Type": "application/json"
                }
            )
            sunucu_cevabi.raise_for_status()
            gelen_veri = sunucu_cevabi.json()
            uretilen_metin = gelen_veri["choices"][0]["message"]["content"]
            loglayici.info("Groq yanıtı başarıyla üretildi.")
            return uretilen_metin.strip()
        except requests.RequestException as hata:
            hata_detayi = ""
            if hasattr(hata, "response") and hata.response is not None:
                hata_detayi = f" -> API Yanıtı: {hata.response.text}"
            loglayici.error(f"Groq API ağ hatası: {hata}{hata_detayi}")
            raise YapayZekaServisHatasi(f"Groq servisine ulaşılamadı: {hata}{hata_detayi}")
        except (KeyError, IndexError, TypeError) as hata:
            loglayici.error(f"Groq yanıt ayrıştırma hatası: {hata}")
            raise YapayZekaServisHatasi(f"Groq yanıtı okunamadı: {hata}")

    def _gemini_cagir(self, kullanici_mesaji: str, gecmis: list) -> str:
        api_anahtari = current_app.config.get("GEMINI_API_KEY", "")

        if not api_anahtari:
            loglayici.warning("GEMINI_API_KEY ayarlanmamış! Demo modu devrede.")
            return self._demo_yaniti_ver(kullanici_mesaji)

        baglanti_adresi = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

        if api_anahtari.startswith("AIzaSy"):
            baglanti_adresi += f"?key={api_anahtari}"
            istek_basliklari = {"Content-Type": "application/json"}
        else:
            istek_basliklari = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_anahtari,
            }

        sistem_talimati = self._sistem_talimati_olustur()
        icerik_paketi = [{"role": m.get("role", "user"), "parts": [{"text": m.get("content", "")}]} for m in gecmis]
        icerik_paketi.append({
            "role": "user",
            "parts": [{"text": f"{sistem_talimati}\n\nKullanıcı Mesajı: {kullanici_mesaji}"}]
        })

        gonderilecek_veri = {
            "contents": icerik_paketi,
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500, "topP": 0.95}
        }

        try:
            sunucu_cevabi = requests.post(
                baglanti_adresi,
                json=gonderilecek_veri,
                timeout=20,
                headers=istek_basliklari
            )
            sunucu_cevabi.raise_for_status()
            gelen_veri = sunucu_cevabi.json()
            uretilen_metin = gelen_veri["candidates"][0]["content"]["parts"][0]["text"]
            return uretilen_metin.strip()
        except Exception as hata:
            hata_detayi = f" -> {hata.response.text}" if hasattr(hata, "response") and hata.response is not None else ""
            loglayici.error(f"Gemini API Hatası: {hata}{hata_detayi}")
            raise YapayZekaServisHatasi(f"Gemini servisine ulaşılamadı: {hata}{hata_detayi}")

    def _openai_cagir(self, kullanici_mesaji: str, gecmis: list) -> str:
        api_anahtari = current_app.config.get("OPENAI_API_KEY", "")

        if not api_anahtari:
            loglayici.warning("OPENAI_API_KEY ayarlanmamış! Demo modu devrede.")
            return self._demo_yaniti_ver(kullanici_mesaji)

        baglanti_adresi = "https://api.openai.com/v1/chat/completions"
        mesajlar_dizisi = [{"role": "system", "content": self._sistem_talimati_olustur()}]
        for mesaj in gecmis:
            mesajlar_dizisi.append({"role": mesaj.get("role", "user"), "content": mesaj.get("content", "")})
        mesajlar_dizisi.append({"role": "user", "content": kullanici_mesaji})

        gonderilecek_veri = {
            "model": "gemma2-9b-it",
            "messages": mesajlar_dizisi,
            "max_tokens": 500,
            "temperature": 0.7,
        }

        try:
            sunucu_cevabi = requests.post(
                baglanti_adresi,
                json=gonderilecek_veri,
                timeout=20,
                headers={
                    "Authorization": f"Bearer {api_anahtari}",
                    "Content-Type": "application/json"
                }
            )
            sunucu_cevabi.raise_for_status()
            gelen_veri = sunucu_cevabi.json()
            uretilen_metin = gelen_veri["choices"][0]["message"]["content"]
            return uretilen_metin.strip()
        except Exception as hata:
            hata_detayi = f" -> {hata.response.text}" if hasattr(hata, "response") and hata.response is not None else ""
            loglayici.error(f"OpenAI API Hatası: {hata}{hata_detayi}")
            raise YapayZekaServisHatasi(f"OpenAI servisine ulaşılamadı: {hata}{hata_detayi}")

    def _demo_yaniti_ver(self, kullanici_mesaji: str) -> str:
        return (
            "Sistem şu anda demo modunda çalışmaktadır. "
            "Lütfen .env dosyanızdaki API anahtarlarını (GROQ_API_KEY vb.) kontrol ediniz."
        )


# Singleton erişim nesneleri
yapay_zeka_servisi = YapayZekaServisi()
ai_service = yapay_zeka_servisi
AIService = YapayZekaServisi