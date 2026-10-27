// Posterler server proxy'sinden gelir — client hiçbir dış servise bağlanmaz (madde 6).
// /api/poster/{imdbId} metahub/TMDb posterini server üzerinden döndürür.

import { API } from "./api";

export function getPosterUrl(imdbId: string): string | null {
  if (!imdbId || imdbId === "tt0000000") return null;
  return `${API.base}/api/poster/${imdbId}`;
}

// Tür bazlı gradient — poster yüklenemezse gösterilir (kırmızı/siyah/bordo paleti)
const GENRE_GRADIENTS: Record<string, string> = {
  Drama: "linear-gradient(135deg,#2a1216 0%,#0d0608 100%)",
  Crime: "linear-gradient(135deg,#1a0608 0%,#0a0304 100%)",
  Action: "linear-gradient(135deg,#3a0a10 0%,#140406 100%)",
  "Sci-Fi": "linear-gradient(135deg,#221c3a 0%,#0d0a1a 100%)",
  Thriller: "linear-gradient(135deg,#1c0c12 0%,#0a0508 100%)",
  Animation: "linear-gradient(135deg,#2a1020 0%,#140810 100%)",
  Comedy: "linear-gradient(135deg,#3a1428 0%,#180a12 100%)",
  Fantasy: "linear-gradient(135deg,#2a0c2a 0%,#120512 100%)",
  Adventure: "linear-gradient(135deg,#2a1410 0%,#120806 100%)",
  Horror: "linear-gradient(135deg,#240608 0%,#0c0203 100%)",
  Romance: "linear-gradient(135deg,#3a0e2a 0%,#180614 100%)",
  Documentary: "linear-gradient(135deg,#1a1a1a 0%,#0a0a0a 100%)",
};

export function posterGradient(genres: string): string {
  const first = genres.split("|")[0];
  return GENRE_GRADIENTS[first] ?? "linear-gradient(135deg,#2a1216 0%,#0d0608 100%)";
}
