// "Bugün ne izlemek istersin?" modalı ve kullanıcının tür tercihi.
// Sayfa yenilenince gösterilmez; server yeniden başladıysa her zaman, aksi halde
// günde bir kez gösterilir.

const SESSION_KEY = "movimind:tonight:shown";  // sessionStorage: sekme kapanınca sıfırlanır
const BOOT_KEY    = "movimind:tonight:boot_id";
const DATE_KEY    = "movimind:tonight:date";
const PREF_KEY    = "movimind:tonight:pref";   // { genre, date }

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

/** Modal bu açılışta gösterilmeli mi (dosya başındaki kurala göre). */
export function shouldShowModal(bootId: string): boolean {
  if (sessionStorage.getItem(SESSION_KEY)) return false;

  const storedBoot = localStorage.getItem(BOOT_KEY);
  const storedDate = localStorage.getItem(DATE_KEY);

  return storedBoot !== bootId || storedDate !== today();
}

/** Modalı bu oturum ve bu gün için gösterildi olarak işaretler. */
export function markModalShown(bootId: string): void {
  sessionStorage.setItem(SESSION_KEY, "1");
  localStorage.setItem(BOOT_KEY, bootId);
  localStorage.setItem(DATE_KEY, today());
}

export interface TonightPref {
  genre: string;
  date: string;
}

export function getPreference(): TonightPref | null {
  try {
    const raw = localStorage.getItem(PREF_KEY);
    return raw ? (JSON.parse(raw) as TonightPref) : null;
  } catch {
    return null;
  }
}

export function setPreference(genre: string): void {
  localStorage.setItem(PREF_KEY, JSON.stringify({ genre, date: today() }));
}
