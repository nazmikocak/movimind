# Kod Stili Kuralları

- **Yorumlar:** `comments.md` standardına göre (neden'i anlat, kodu tekrar etme).
- **Emoji yok:** Hiçbir UI metninde/JSX'te emoji kullanma. İkon gerekiyorsa
  `react-icons/lu` (Lucide) içe aktar.
- **Öklid KNN:** Benzerlik/mesafe her zaman Öklid. `metric="cosine"` ekleme.
- **Tek API köprüsü:** Frontend'de `fetch`/`axios` yalnızca `services/api.ts` içinde,
  yalnızca `VITE_API_BASE`'e. Bileşenlerden doğrudan ağ çağrısı yok.
- **Dış servisler server'da:** TMDb/OMDb vb. her API çağrısı `server/app/services/`.
- **Veritabanı:** ORM ve ham SQL yok; `fn_*`/`sp_*` çağrıları yalnızca
  `server/app/db/repository.py` içinde (ayrıntı: `database.md`).
- **Tema token'ları:** SCSS'te ham hex yerine `_variables.scss` değişkenleri.
- **Türkçe arayüz metni**, kod/değişken adları İngilizce.
- **Yapılandırma .env'den:** eşik, anahtar, port gibi değerleri koda gömme.
