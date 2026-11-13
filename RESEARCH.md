# Haftalık araştırma rehberi (zamanlanmış görev bunu izler)

Kurallar
- Yalnızca resmî ya da kurumsal kaynaklardan bilgi al; her değişikliğin kaynağını PR açıklamasına yaz.
- Tutar, tarih, yaş sınırı, hak koşulu değişiklikleri **ayrı başlıkta** listelenir ("Önemli değişiklikler").
- Emin olmadığın bilgiyi ekleme; "kontrol edilemedi" diye not düş.
- `checked` alanlarını kontrol tarihine güncelle.
- `python3 scripts/validate.py` geçmeden PR açma.
- Video için yalnızca doğrudan açılabildiği doğrulanan bağlantılar (`type: video/playlist`) ya da YouTube arama bağlantıları (`type: search`). Çocuk içeriğinde resmî/kurumsal kanalları tercih et.

Kurallar dosyası (rules.json, uygulama 4.0+)
- Araç muayenesi, trafik vergisi, yol vinyeti, kazan bakımı, vergi beyanı tarihleri, kreş vergi indirimi, schooltoeslag ödeme günleri, diş (mondzorgtraject).
- Her yıl: **vergi beyanı tarihleri** (`tax_deadline.dates`, `tax_open`) — FOD Financiën açıklayınca yeni yılın tarihlerini ekle; **schooltoeslag ödeme günleri** (yeni okul yılı); **kreş indirimi günlük üst sınırı** (gelir yılı değişince).
- Kural değişince (ör. muayene aralığı, kazan bakımı) `months`/metni güncelle ve `source` bağlantısını doğrula. Her resmî kural https kaynak gerektirir.
- `checked` tarihini güncelle. Uygulama bu dosyayı yalnızca v2 akışından (4.0+) alır.

Kaynaklar
| Konu | Kaynak |
|---|---|
| Çocuk parası (Flaman) | groeipakket.be, Opgroeien |
| Çocuk parası (Brüksel) | famiris.brussels, Iriscare |
| Çocuk parası (Valon) | famiwal.be, AVIQ |
| Okul tatilleri | vlaanderen.be (schoolvakanties), enseignement.be / gallilex.cfwb.be |
| Resmî tatiller | belgium.be |
| Aşı takvimi | kindengezin.be / opgroeien.be, one.be, vaccination-info.be |
| İzinler, vergi | rva.be / onem.be, fin.belgium.be (MyMinfin) |
| Okul masrafı / burs | onderwijs.vlaanderen.be (studietoelagen), enseignement.be (allocations d'études) |
| Ulaşım | belgiantrain.be, delijn.be, stib.be, letec.be |
| Türk bayramları | diyanet.gov.tr (dini günler takvimi) |
| Konsolosluk | Brüksel / Anvers Başkonsoloslukları, konsolosluk.gov.tr |
| Araç muayenesi, vergi, vinyet | vlaanderen.be (technische keuring, verkeersbelastingen, wegenvignet), GOCA, AutoSécurité, Touring |
| Kazan bakımı | vlaanderen.be (verplicht onderhoud cv-installatie), environnement.brussels, energie.wallonie.be |
| Vergi beyanı, kreş indirimi | fin.belgium.be, wikifin.be |
| Diş geri ödemesi | riziv.fgov.be / inami.fgov.be (mondzorgtraject) |
| Dil öğrenme | vdab.be, Huis van het Nederlands, Lire et Écrire, TRT Çocuk, Ketnet |
