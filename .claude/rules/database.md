# Veritabanı Kuralları

Veritabanı: **Neon (PostgreSQL)**. Sürücü: **psycopg 3** (+ `psycopg-pool`).
Yerel geliştirme `dev` branch'ine, canlı `production` branch'ine bağlanır.

## Script'ler (kök `database/` klasörü)

Flyway tarzı sürümlü dosyalar; sırayla, her biri **bir kez** uygulanır:

| Dosya | İçerik |
|---|---|
| `V1__init.sql` | Enum tipleri, tablolar, index'ler, kısıtlar |
| `V2__procedures.sql` | DML yapan procedure'ler (`sp_*`) |
| `V3__functions.sql` | Değer döndüren function'lar (`fn_*`) |
| `V4__triggers.sql` | Trigger'lar ve trigger function'ları (`trg_*`) |

- **Canlıya geçene kadar** V1–V4 doğrudan düzenlenir (yeni V dosyası açılmaz); `dev` branch'i sıfırlanıp yeniden
  yayınlanır (kullanıcı kararı). Canlı (`production`) kurulduktan sonra:
- Uygulanmış bir V dosyası **değiştirilmez**. Her değişiklik yeni bir dosyayla yapılır:
  `V5__add_movie_index.sql`, `V6__update_fn_get_movies.sql` ... Function/procedure
  güncellemesi yeni dosyada `CREATE OR REPLACE` ile yazılır.
- `server/app/db/migrations.py` dosyaları sırayla uygular ve `schema_migrations`
  tablosunda sağlama toplamıyla (checksum) tutar. Uygulanmış dosya değişirse hata verir.
- Migration'lar yerel yayın adımında otomatik çalışır (`python main.py` -> dev,
  `python main.py --publish-production` -> canlı). Canlı server DDL çalıştırmaz.

## ORM ve Ham SQL Yasağı

- ORM kullanılmaz (SQLAlchemy, Django ORM, Peewee, Tortoise vb.).
- Uygulama kodunda ham SQL yazılmaz (`SELECT ... FROM tablo`, `INSERT`, `UPDATE`,
  `DELETE`, DDL). Tüm işlemler function/procedure üzerinden yapılır:
  - Okuma: `SELECT * FROM fn_get_movies()`
  - Yazma: `CALL sp_set_meta(%s::app_meta_key, %s, NULL)`
- Veritabanı çağrıları **yalnızca** `server/app/db/repository.py` içindedir.
- Tek istisna `server/app/db/migrations.py`: script dosyalarını ve kendi
  `schema_migrations` kaydını çalıştırır.
- Parametreler her zaman `%s` ile bağlanır; SQL metni string birleştirmeyle kurulmaz.

## PostgreSQL İsimlendirme

- `fn_*` -> değer döndüren, yan etkisiz function (`RETURNS TABLE`, `STABLE`)
  -> `SELECT * FROM fn_...(...)`
- `sp_*` -> DML yapan procedure -> `CALL sp_...(...)`. Sonuç gerekiyorsa
  `INOUT o_*` parametresiyle döner (ör. `o_inserted`, `o_updated_at`).
- `trg_*` -> trigger (`trg_<tablo>_<amaç>`) ve trigger function'ı (`trg_fn_<amaç>`).
- Parametreler `p_`, çıktılar `o_` ön ekli. Tablo/kolon adları `snake_case`, tablolar çoğul.

## Repository Dönüş Tipleri

- **`get_*` metotları** her zaman **`T | None`** döner. Kayıt bulunamazsa veya liste/
  sözlük boşsa `None` döner. `None` kontrolü ve hata fırlatma **servis katmanının**
  (`model/recommender.py`, `services/external.py`, `model/publish.py`) sorumluluğudur.
- **Create / Update / Upsert** metotları `None` döndürmez: yazılan kaydı ya da toplu
  işlemlerde etkilenen satır sayısını döndürür.
- **Delete** metotları `None` döner.

## Mapper

- Veritabanı satırı -> uygulama nesnesi dönüşümü `server/app/db/mappers.py`'deki saf
  fonksiyonlarla yapılır (`movie_from_row`, `meta_from_rows` ...).
- Repository satırdan elle sözlük kurmaz; mapper'ı çağırır. API alan adları
  (`movieId`, `imdbId` ...) yalnızca mapper'da tanımlanır.

## İlişkili Veri

- Birden fazla tablodan gelen veri, birden fazla repository çağrısıyla değil,
  function içinde **JOIN** ile tek sorguda alınır. Mapper satırları okuyup iç
  koleksiyonu doldurur.

## Enum Tipleri

- Sabit değer kümeleri DB seviyesinde `ENUM` olarak tanımlanır. Tek veritabanı
  (`public`) olduğu için şema ön eki kullanılmaz:

  ```sql
  CREATE TYPE app_meta_key AS ENUM ('analysis', 'dataset_stats', 'model_info', ...);
  CREATE TABLE app_meta (key app_meta_key PRIMARY KEY, ...);
  ```

- Python tarafında aynı değerler `server/app/db/enums.py`'de `StrEnum` olarak tutulur;
  koddaki anahtarlar string değil enum üyesidir (`MetaKey.MODEL_VERSION`).
- Yeni değer yeni bir V dosyasında eklenir: `ALTER TYPE app_meta_key ADD VALUE '...';`
