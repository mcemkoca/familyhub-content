# FamilyHub içerik akışı

FamilyHub uygulamasının kendini güncelleyen içeriği: Belçika hakları ve tutarları, okul tatilleri ve özel günler, yaşam takvimi, Türkçe / Hollandaca / Fransızca kartları, öğrenme bağlantıları. **Kişisel veri yoktur.**

## Nasıl çalışır
1. Haftalık araştırma görevi resmî kaynakları kontrol eder, `content/` içindeki dosyaları günceller ve **bir pull request açar**. Kısa özet Dante ile gelir.
2. Değişikliği GitHub uygulamasında okuyup **Merge** derseniz yayına girer. Merge edilmeyen hiçbir şey yayımlanmaz.
3. `Publish content` iş akışı içeriği doğrular (`scripts/validate.py`), imzalar (`FEED_PRIVATE_KEY` gizli anahtarı, ECDSA P-256) ve GitHub Pages'e koyar: `https://mcemkoca.github.io/familyhub-content/v1/manifest.json`.
4. Telefonlar haftada bir imzayı ve her dosyanın SHA-256 özetini doğrular, içeriği deneme yüklemesinden geçirir, sorun yoksa geçer. Uygulama kodu bu yolla asla değişmez.

Tek seferlik kurulum: Settings → Pages → Source: **GitHub Actions**. Settings → Secrets → Actions: `FEED_PRIVATE_KEY`.

Kaynak listesi ve kurallar: [RESEARCH.md](RESEARCH.md).
