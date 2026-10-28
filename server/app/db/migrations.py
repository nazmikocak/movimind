"""Kök `database/` klasöründeki sürümlü SQL script'lerini sırayla uygular.

Her `V<n>__<ad>.sql` bir kez çalışır ve `schema_migrations` tablosuna sağlama
toplamıyla kaydedilir. Ham SQL'in çalıştığı tek modül budur (bkz. database.md).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import psycopg

from app.config import config

_SCRIPT_NAME = re.compile(r"^V(\d+)__\w+\.sql$")


def _scripts() -> list[tuple[int, Path]]:
    found = []
    for path in config.DB_MIGRATIONS_DIR.glob("V*__*.sql"):
        match = _SCRIPT_NAME.match(path.name)
        if match:
            found.append((int(match.group(1)), path))
    return sorted(found)


def migrate(conn: psycopg.Connection) -> list[str]:
    """Bekleyen script'leri uygular; uygulananların adlarını döndürür."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version    integer PRIMARY KEY,
            script     text        NOT NULL,
            checksum   text        NOT NULL,
            applied_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    applied = dict(conn.execute("SELECT version, checksum FROM schema_migrations").fetchall())

    done = []
    for version, path in _scripts():
        # CRLF/LF farkı aynı dosyanın checksum'ını değiştirmesin
        sql = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        checksum = hashlib.sha256(sql.encode("utf-8")).hexdigest()
        if version in applied:
            if applied[version] != checksum:
                raise RuntimeError(
                    f"{path.name} uygulandıktan sonra değiştirilmiş. "
                    "Değişikliği yeni bir V dosyasıyla yapın."
                )
            continue
        with conn.transaction():
            conn.execute(sql)
            conn.execute(
                "INSERT INTO schema_migrations (version, script, checksum) VALUES (%s, %s, %s)",
                (version, path.name, checksum),
            )
        print(f"[db] Uygulandı -> {path.name}")
        done.append(path.name)
    return done
