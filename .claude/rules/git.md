# Git Kuralları

- **Commit ve push'u her zaman kullanıcı yapar.** Claude `git commit`, `git push`,
  `git tag` veya geçmişi değiştiren komut çalıştırmaz; yalnızca commit mesajı önerir.
- Mesajlar **Conventional Commits 1.0.0** biçiminde ve **İngilizce** yazılır:

  ```text
  type(scope): short summary in imperative mood

  - first change in the body as a bullet
  - second change
  ```

  - **Başlık:** `type(scope): summary`. Küçük harfle başlar, emir kipinde ("add", "fix"),
    sonunda nokta yok, en fazla 72 karakter. `scope` isteğe bağlı: `client`, `server`,
    `db`, `model`, `ci`, `docker`, `docs` ...
  - **Gövde:** başlıktan sonra bir boş satır, ardından her değişiklik `- ` ile ayrı madde.
  - **Türler:** `feat`, `fix`, `refactor`, `perf`, `style`, `docs`, `test`, `build`,
    `ci`, `chore`, `revert`.
  - **Kırıcı değişiklik:** başlıkta `type!:` ve gövdenin sonunda `BREAKING CHANGE: ...`.
- Değişiklikler mantıklı parçalara bölünür; her öneriyle birlikte o commit'e girecek
  dosyaların listesi verilir.
