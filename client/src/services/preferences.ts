// "Bugün ne izlemek istersin?" modalı + kullanıcı tür tercihi.
//
// Gösterim kuralı:
//   - Sayfa yenilemede ASLA gösterme  (sessionStorage bayrağı)
//   - Server yeniden başlatıldıysa HER ZAMAN göster (boot_id değişti)
//   - Aynı boot_id ile günde 1 kez göster (tarih değişti)

const SESSION_KEY = "movimind:tonight:shown";    // sessionStorage — sekme kapanınca sıfırlanır
const BOOT_KEY    = "movimind:tonight:boot_id";   // localStorage
const DATE_KEY    = "movimind:tonight:date";       // localStorage
const PREF_KEY    = "movimind:tonight:pref";       // localStorage — { genre, date }

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

/**
 * Verilen boot_id ile modalın gösterilip gösterilmeyeceğini döndürür.
 * Sayfa yenilemede (sessionStorage dolu) false.
 * Server yeniden başlatıldıysa veya yeni gün ise true.
 */
export function shouldShowModal(bootId: string): boolean {
  if (sessionStorage.getItem(SESSION_KEY)) return false;

  const storedBoot = localStorage.getItem(BOOT_KEY);
  const storedDate = localStorage.getItem(DATE_KEY);

  return storedBoot !== bootId || storedDate !== today();
}

/** Modal gösterildi olarak işaretle (sessionStorage + localStorage güncelle). */
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
