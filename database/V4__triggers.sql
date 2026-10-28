-- V4: Trigger'lar (trg_*) — güncellenen satırın updated_at alanını otomatik yeniler

CREATE OR REPLACE FUNCTION trg_fn_set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_app_meta_updated_at
    BEFORE UPDATE ON app_meta
    FOR EACH ROW EXECUTE FUNCTION trg_fn_set_updated_at();

CREATE TRIGGER trg_external_cache_updated_at
    BEFORE UPDATE ON external_cache
    FOR EACH ROW EXECUTE FUNCTION trg_fn_set_updated_at();
