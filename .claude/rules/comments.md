# Yorum Kuralları

Dayanak: Python için **PEP 8** (Comments) ve **PEP 257** (Docstrings), TypeScript için
**TSDoc**, genel ilke olarak *Clean Code* (R. C. Martin, 4. bölüm).

**Temel ilke:** Kod *ne* yaptığını adlarla ve yapıyla kendisi anlatır. Yorum yalnızca
koddan okunamayanı açıklar: *neden* böyle yapıldığını, bir kısıtı, bir uyarıyı.

## Yazılır

- **Dosya başı açıklaması:** dosyanın sorumluluğu, tek cümle; gerekiyorsa kısa bir paragraf.
- **Davranışı adından anlaşılmayan** public fonksiyon, sınıf, hook veya bileşen için
  docstring/TSDoc.
- **Neden / kısıt / uyarı:** iş kuralı, dış servisin beklenmedik davranışı, performans
  tercihi, sürüm bağımlılığı, geçici çözüm.
- **Hukuki ve atıf notları** (lisans, veri kaynağı koşulları).

## Yazılmaz

- Kodu tekrar eden yorum: `# Kaydet`, `{/* Butonlar */}`, `// Poster`.
- Bölüm ayraçları ve süslü başlıklar: `# ── Model ──────`, `// =====`.
- Yorum satırına alınmış kod.
- Geçmiş ve günlük notları: "eskiden ...", "madde 6", "yeni eklendi".
- Değişken veya fonksiyon adının zaten söylediğini anlatan satır sonu yorumu.

## Biçim

| Dosya | Biçim |
|---|---|
| Python | Dosya ve fonksiyon açıklaması `"""..."""` (PEP 257: tek satır özet, nokta ile biter; gerekiyorsa boş satır + ayrıntı). Satır içi `# ` yorumu koddan en az iki boşluk sonra, kısa. |
| TS / TSX | Dışa açılan ve davranışı açık olmayan öğeler için `/** ... */` (TSDoc). Diğer açıklamalar `//`. JSX içinde yorum yalnızca gerçek bir uyarı için. |
| SCSS | `//` yalnızca açık olmayan değerler için (sabit sayılar, tarayıcı geçici çözümleri). |
| SQL | Dosya başında tek satır amaç; `--` yalnızca açık olmayan kolon veya mantık için. |
| Yapılandırma (`.env.example`, Dockerfile, YAML, `.gitignore`) | Açık olmayan ayarın üstünde tek satır `#`. Grup başlığı süssüz tek satır: `# Veritabanı`. |

- Dil Türkçe; kısa ve tam cümle. Kod öğeleri backtick ile yazılır: `knn_model.pkl`.
- Yorum kodla birlikte güncellenir; yanlış yorum, yorumsuz koddan kötüdür.
