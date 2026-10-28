import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Lottie, { type LottieRefCurrentProps } from "lottie-react";
import { LuChevronsUpDown } from "react-icons/lu";
import type { Movie } from "../../types/movie";
import { API } from "../../services/api";
import MovieCard from "../../components/MovieCard/MovieCard";
import searchAnimation from "../../assets/animation/SearchLottie.json";
import "./RecommendPage.scss";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";

const STORAGE_KEY = "movimind:recommend:state";

interface SavedState {
  selectedGenres: string[];
  minRating: number;
  maxRating: number;
  yearMin: string;
  yearMax: string;
  count: number;
  sort: string;
  minVotes: number;
  movieQuery: string;
  movieId: number | null;
  results: Movie[];
  searched: boolean;
}

function loadState(): SavedState | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as SavedState) : null;
  } catch {
    return null;
  }
}

function saveState(s: SavedState) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  } catch { /* ignore quota errors */ }
}

const GENRES = [
  "Action", "Adventure", "Animation", "Comedy", "Crime",
  "Documentary", "Drama", "Fantasy", "Horror", "Mystery",
  "Romance", "Sci-Fi", "Thriller", "War",
];

const GENRE_TR: Record<string, string> = {
  Action: "Aksiyon", Adventure: "Macera", Animation: "Animasyon",
  Comedy: "Komedi", Crime: "Suç", Documentary: "Belgesel", Drama: "Dram",
  Fantasy: "Fantastik", Horror: "Korku", Mystery: "Gizem", Romance: "Romantik",
  "Sci-Fi": "Bilim Kurgu", Thriller: "Gerilim", War: "Savaş",
};

const SORTS: { key: string; label: string }[] = [
  { key: "rating", label: "Puana Göre" },
  { key: "popularity", label: "İzlenmeye Göre" },
  { key: "year", label: "En Yeniler" },
  { key: "title", label: "A'dan Z'ye" },
];

export default function RecommendPage() {
  useDocumentTitle("Film Önerileri");
  const navigate = useNavigate();

  const saved = loadState();

  const [selectedGenres, setSelectedGenres] = useState<string[]>(saved?.selectedGenres ?? []);
  const [minRating, setMinRating] = useState(saved?.minRating ?? 0);
  const [maxRating, setMaxRating] = useState(saved?.maxRating ?? 5);
  const [yearMin, setYearMin] = useState(saved?.yearMin ?? "");
  const [yearMax, setYearMax] = useState(saved?.yearMax ?? "");
  const [count, setCount] = useState(saved?.count ?? 10);
  const [sort, setSort] = useState(saved?.sort ?? "rating");
  const [minVotes, setMinVotes] = useState(saved?.minVotes ?? 0);
  const [movieQuery, setMovieQuery] = useState(saved?.movieQuery ?? "");
  const [movieId, setMovieId] = useState<number | null>(saved?.movieId ?? null);

  const [suggestions, setSuggestions] = useState<Movie[]>([]);
  const [showSuggest, setShowSuggest] = useState(false);
  const suggestRef = useRef<HTMLDivElement>(null);

  const [results, setResults] = useState<Movie[]>(saved?.results ?? []);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(saved?.searched ?? false);
  const lottieRef = useRef<LottieRefCurrentProps>(null);
  const resultsRef = useRef<HTMLElement>(null);

  // Tüm katalogda arar; yazma bitene kadar istek atılmaz
  useEffect(() => {
    const q = movieQuery.trim();
    if (!q) { setSuggestions([]); return; }
    let cancelled = false;
    const timer = setTimeout(() => {
      API.search(q, 8)
        .then((list) => { if (!cancelled) setSuggestions(list); })
        .catch(() => { if (!cancelled) setSuggestions([]); });
    }, 250);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [movieQuery]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (suggestRef.current && !suggestRef.current.contains(e.target as Node))
        setShowSuggest(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const toggleGenre = (g: string) => {
    setSelectedGenres((prev) =>
      prev.includes(g) ? prev.filter((x) => x !== g) : [...prev, g]
    );
  };

  // Filtreler sessionStorage'da tutulur; sayfaya geri dönünce korunur
  useEffect(() => {
    saveState({
      selectedGenres, minRating, maxRating, yearMin, yearMax,
      count, sort, minVotes, movieQuery, movieId, results, searched,
    });
  }, [selectedGenres, minRating, maxRating, yearMin, yearMax,
      count, sort, minVotes, movieQuery, movieId, results, searched]);

  const runSearch = useCallback(async (sortKey: string) => {
    setLoading(true);
    setSearched(true);
    try {
      const params: Record<string, string | number> = { n: count, sort: sortKey };
      if (selectedGenres.length > 0) params.genre = selectedGenres.join(",");
      if (minRating > 0) params.min_rating = minRating;
      if (maxRating < 5) params.max_rating = maxRating;
      if (yearMin) params.year_min = Number(yearMin);
      if (yearMax) params.year_max = Number(yearMax);
      if (minVotes > 0) params.min_votes = minVotes;
      if (movieId) params.movie_id = movieId;
      setResults(await API.recommend(params));
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [selectedGenres, minRating, maxRating, yearMin, yearMax, count, minVotes, movieId]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    runSearch(sort);
    // Mobilde sonuçlar filtrelerin altında kalır; görünür alana kaydır
    if (window.matchMedia("(max-width: 768px)").matches) {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  // Sonuçlar açıkken sıralama değişirse liste yeniden istenir
  const handleSortChange = (key: string) => {
    setSort(key);
    if (searched) runSearch(key);
  };

  const handleReset = () => {
    setSelectedGenres([]); setMinRating(0); setMaxRating(5);
    setYearMin(""); setYearMax(""); setCount(10); setSort("rating");
    setMinVotes(0); setMovieQuery(""); setMovieId(null);
    setResults([]); setSearched(false);
    sessionStorage.removeItem(STORAGE_KEY);
  };

  return (
    <div className="rec-page page-container">
      <div className="rec-page__header">
        <h1 className="rec-page__title">Film Önerileri</h1>
        <div className="rec-page__header-row">
          <p className="rec-page__sub">
            Türe, yıla ya da beğendiğin bir filme göre kişiselleştirilmiş
            öneriler al.
          </p>
          <div className="rec-main__sort">
            <LuChevronsUpDown className="rec-main__sort-icon" />
            <select
              id="rec-sort"
              className="rec-main__sort-select"
              value={sort}
              onChange={(e) => handleSortChange(e.target.value)}
            >
              {SORTS.map(({ key, label }) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="recommend">
      <aside className="rec-filter">
        <div className="rec-filter__title">Kriterler</div>

        <form onSubmit={handleSubmit}>

          <div className="rec-filter__field">
            <label className="rec-filter__label">
              Film Türü
              {selectedGenres.length > 0 && (
                <span className="rec-filter__label-val">{selectedGenres.length} seçili</span>
              )}
            </label>
            <div className="rec-filter__genre-pills">
              {GENRES.map((g) => (
                <button
                  key={g}
                  type="button"
                  className={`rec-filter__genre-pill${selectedGenres.includes(g) ? " rec-filter__genre-pill--active" : ""}`}
                  onClick={() => toggleGenre(g)}
                >
                  {GENRE_TR[g] ?? g}
                </button>
              ))}
            </div>
          </div>

          <div className="rec-filter__field">
            <label className="rec-filter__label">
              Minimum Puan
              <span className="rec-filter__label-val">
                {minRating > 0 ? minRating.toFixed(1) : "—"}
              </span>
            </label>
            <input
              type="range"
              className="rec-filter__range"
              min={0} max={5} step={0.5}
              value={minRating}
              onChange={(e) => setMinRating(Number(e.target.value))}
            />
          </div>

          <div className="rec-filter__field">
            <label className="rec-filter__label">
              Maksimum Puan
              <span className="rec-filter__label-val">
                {maxRating < 5 ? maxRating.toFixed(1) : "—"}
              </span>
            </label>
            <input
              type="range"
              className="rec-filter__range"
              min={0} max={5} step={0.5}
              value={maxRating}
              onChange={(e) => setMaxRating(Number(e.target.value))}
            />
          </div>

          <div className="rec-filter__field">
            <label className="rec-filter__label">
              Minimum Oy Sayısı
              <span className="rec-filter__label-val">
                {minVotes > 0 ? minVotes.toLocaleString("tr-TR") : "—"}
              </span>
            </label>
            <input
              type="range"
              className="rec-filter__range"
              min={0} max={5000} step={250}
              value={minVotes}
              onChange={(e) => setMinVotes(Number(e.target.value))}
            />
            <div className="rec-filter__hint rec-filter__hint--muted">
              Daha güvenilir (çok oylanmış) filmler
            </div>
          </div>

          <hr className="rec-filter__divider" />

          <div className="rec-filter__field">
            <label className="rec-filter__label">Yıl Aralığı</label>
            <div className="rec-filter__year-row">
              <input
                className="rec-filter__input"
                type="number"
                placeholder="1970"
                min={1900} max={2025}
                value={yearMin}
                onChange={(e) => setYearMin(e.target.value)}
              />
              <input
                className="rec-filter__input"
                type="number"
                placeholder="2024"
                min={1900} max={2025}
                value={yearMax}
                onChange={(e) => setYearMax(e.target.value)}
              />
            </div>
          </div>

          <div className="rec-filter__field">
            <label className="rec-filter__label">
              Film Sayısı
              <span className="rec-filter__label-val">{count}</span>
            </label>
            <input
              type="range"
              className="rec-filter__range"
              min={5} max={50} step={5}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
            />
          </div>

          <hr className="rec-filter__divider" />

          <div className="rec-filter__field">
            <label className="rec-filter__label">Beğendiğin Film</label>
            <div className="rec-filter__autocomplete" ref={suggestRef}>
              <input
                className="rec-filter__input"
                type="text"
                placeholder="Film adı yazın..."
                value={movieQuery}
                autoComplete="off"
                onChange={(e) => {
                  setMovieQuery(e.target.value);
                  setMovieId(null);
                  setShowSuggest(true);
                }}
                onFocus={() => movieQuery && setShowSuggest(true)}
              />
              {showSuggest && suggestions.length > 0 && (
                <div className="rec-filter__autocomplete-list">
                  {suggestions.map((m) => (
                    <div
                      key={m.movieId}
                      className="rec-filter__autocomplete-item"
                      onMouseDown={(e) => {
                        e.preventDefault();
                        setMovieQuery(m.title);
                        setMovieId(m.movieId);
                        setShowSuggest(false);
                      }}
                    >
                      {m.title}
                      {m.year && (
                        <span className="rec-filter__autocomplete-item-year">
                          {m.year}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
            {movieId && (
              <div className="rec-filter__hint">
                Bu filme benzer izleyici profillerinden öneri getirilir
              </div>
            )}
          </div>

          <button type="submit" className="rec-filter__submit" disabled={loading}>
            {loading ? "Hesaplanıyor..." : "Öneri Al"}
          </button>
          <button type="button" className="rec-filter__reset" onClick={handleReset}>
            Sıfırla
          </button>
        </form>
      </aside>

      <main className="rec-main" ref={resultsRef}>
        {loading && <div className="rec-loading">Öneriler hesaplanıyor...</div>}

        {!loading && !searched && (
          <div className="rec-empty">
            <Lottie
              animationData={searchAnimation}
              loop
              lottieRef={lottieRef}
              onDOMLoaded={() => lottieRef.current?.setSpeed(0.75)}
              className="rec-empty__lottie"
            />
            <div className="rec-empty__text">
              Kriterlerinizi seçin ve "Öneri Al" butonuna basın
            </div>
            <div className="rec-empty__sub">
              Size en uygun filmleri sizin için bir araya getirelim
            </div>
          </div>
        )}

        {!loading && searched && results.length === 0 && (
          <div className="rec-empty">
            <div className="rec-empty__circle" />
            <div className="rec-empty__text">Kriterlere uygun film bulunamadı</div>
            <div className="rec-empty__sub">Filtreleri genişletin veya sıfırlayın</div>
          </div>
        )}

        {!loading && results.length > 0 && (
          <>
            <div className="rec-grid">
              {results.map((m) => (
                <MovieCard
                  key={m.movieId}
                  movie={m}
                  onClick={() => navigate("/movie/" + m.movieId, { state: { movie: m } })}
                />
              ))}
            </div>
            <div className="rec-main__count-row">
              <span className="rec-main__count">{results.length} sonuç</span>
            </div>
          </>
        )}
      </main>
      </div>
    </div>
  );
}
