# Kod Stili Kuralları

- **Emoji yok:** Hiçbir UI metninde/JSX'te emoji kullanma. İkon gerekiyorsa
  `react-icons/lu` (Lucide) içe aktar.
- **Öklid KNN:** Benzerlik/mesafe her zaman Öklid. `metric="cosine"` ekleme.
- **Tek API köprüsü:** Frontend'de `fetch`/`axios` yalnızca `services/api.ts` içinde,
  yalnızca `VITE_API_BASE`'e. Bileşenlerden doğrudan ağ çağrısı yok.
- **Dış servisler server'da:** TMDb/OMDb/poster vb. her dış çağrı `server/app/services/`.
- **Tema token'ları:** SCSS'te ham hex yerine `_variables.scss` değişkenleri.
- **Türkçe arayüz metni**, kod/değişken adları İngilizce.
- **Yapılandırma .env'den:** eşik, anahtar, port gibi değerleri koda gömme.
