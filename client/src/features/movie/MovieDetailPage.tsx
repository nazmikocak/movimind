import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LuArrowLeft, LuStar, LuPlay, LuFilm, LuClock, LuCalendar,
  LuGlobe, LuAward, LuInfo, LuChevronLeft, LuChevronRight, LuX,
} from "react-icons/lu";
import type { Movie, MovieDetails, CastMember } from "../../types/movie";
import { API } from "../../services/api";
import { usePoster } from "../../hooks/usePoster";
import MovieCard from "../../components/MovieCard/MovieCard";
import { localExtensions } from "../../extensions";
import "./MovieDetailPage.scss";

function Stars({ rating }: { rating: number }) {
  return (
    <div className="mp__score-big">
      <LuStar className="mp__score-big-star" />
      <span className="mp__score-big-num">{rating.toFixed(1)}</span>
      <span className="mp__score-big-max">/5</span>
    </div>
  );
}

function RatingBars({ avg, count }: { avg: number; count: number }) {
  const bars = [5, 4, 3, 2, 1].map((star) => {
    const dist = Math.exp(-0.8 * Math.abs(star - avg));
    return { star, pct: Math.round(dist * 100) };
  });
  const total = bars.reduce((s, b) => s + b.pct, 0);
  return (
    <div className="mp__rating-bars">
      <div className="mp__section-title">Tahmini Puan Dağılımı</div>
      {bars.map((b) => (
        <div key={b.star} className="mp__rating-bar-row">
          <span className="mp__rating-bar-label">{b.star}<LuStar /></span>
          <div className="mp__rating-bar-track">
            <div className="mp__rating-bar-fill" style={{ width: `${Math.round((b.pct / total) * 100)}%` }} />
          </div>
          <span className="mp__rating-bar-val">
            {Math.round((count * b.pct) / total).toLocaleString("tr-TR")}
          </span>
        </div>
      ))}
    </div>
  );
}

function CastCard({ member }: { member: CastMember }) {
  const [err, setErr] = useState(false);
  return (
    <div className="mp__cast-card">
      <div className="mp__cast-photo">
        {member.photo && !err ? (
          <img src={member.photo} alt={member.name} onError={() => setErr(true)} loading="lazy" />
        ) : (
          <div className="mp__cast-photo-ph"><LuFilm /></div>
        )}
      </div>
      <div className="mp__cast-name">{member.name}</div>
      {member.character && <div className="mp__cast-char">{member.character}</div>}
    </div>
  );
}

function HeroBg({ movie, backdrop }: { movie: Movie; backdrop?: string | null }) {
  const { url, gradient, onError } = usePoster(0, movie.genres, movie.imdbId);
  const bg = backdrop || url;
  if (bg) return <img className="mp__hero-bg" src={bg} alt="" onError={onError} />;
  return <div className="mp__hero-ph" style={{ background: gradient }} />;
}

function Poster({ movie, tmdbPoster }: { movie: Movie; tmdbPoster?: string | null }) {
  const { url, gradient, onError } = usePoster(0, movie.genres, movie.imdbId);
  const src = tmdbPoster || url;
  if (src) return <img src={src} alt={movie.title} onError={onError} loading="lazy" />;
  return <div className="mp__poster-ph" style={{ background: gradient }}><LuFilm /></div>;
}

function scrollState(ref: React.RefObject<HTMLDivElement | null>,
  setL: (v: boolean) => void, setR: (v: boolean) => void) {
  const el = ref.current;
  if (!el) return;
  setL(el.scrollLeft > 8);
  setR(el.scrollWidth - el.clientWidth - el.scrollLeft > 8);
}

export default function MovieDetailPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const passedMovie = location.state?.movie as Movie | undefined;

  const [details, setDetails] = useState<MovieDetails | null>(null);
  const [similar, setSimilar] = useState<Movie[]>([]);
  const [showTrailer, setShowTrailer] = useState(false);

  const castScrollRef = useRef<HTMLDivElement>(null);
  const similarScrollRef = useRef<HTMLDivElement>(null);
  const [castLeft, setCastLeft] = useState(false);
  const [castRight, setCastRight] = useState(false);
  const [simLeft, setSimLeft] = useState(false);
  const [simRight, setSimRight] = useState(false);

  const movie: Movie | null = (details as Movie | null) ?? passedMovie ?? null;
  const ext = details?.external;

  useEffect(() => {
    if (!passedMovie) return;
    const id = passedMovie.movieId;
    API.movieDetails(id).then(setDetails).catch(() => {});
    API.similar(id, 10).then(setSimilar).catch(() => {});
    window.scrollTo(0, 0);
  }, [passedMovie?.movieId]);

  useEffect(() => {
    scrollState(castScrollRef, setCastLeft, setCastRight);
    scrollState(similarScrollRef, setSimLeft, setSimRight);
  }, [details, similar.length]);

  if (!movie) {
    return (
      <div className="mp__empty">
        Film bulunamadı.
        <button className="mp__back-btn" onClick={() => navigate(-1)}>
          <LuArrowLeft /> Geri dön
        </button>
      </div>
    );
  }

  const tags = movie.tags ? movie.tags.split(",").map((t) => t.trim()).filter(Boolean).slice(0, 20) : [];
  const cast = ext?.cast ?? [];

  return (
    <div className="mp">
      {/* Hero backdrop */}
      <div className="mp__hero">
        <HeroBg movie={movie} backdrop={ext?.backdrop} />
        <div className="mp__hero-overlay" />
      </div>

      {/* Ana içerik */}
      <div className="mp__body page-container">
        <div className="mp__poster">
          <Poster movie={movie} tmdbPoster={ext?.poster} />
        </div>

        <div className="mp__info">
          <h1 className="mp__title">{movie.title}</h1>
          {ext?.tagline && <p className="mp__tagline">{ext.tagline}</p>}

          {/* Puanlar */}
          <div className="mp__scores">
            <Stars rating={movie.avg_rating} />
            {ext?.imdb_rating && (
              <div className="mp__ext-score mp__ext-score--imdb">
                <span className="mp__ext-score-label">IMDb</span>
                <span className="mp__ext-score-val">{ext.imdb_rating}</span>
                {ext.imdb_votes && <span className="mp__ext-score-votes">{ext.imdb_votes} oy</span>}
              </div>
            )}
            {ext?.metascore && (
              <div className="mp__ext-score mp__ext-score--meta">
                <span className="mp__ext-score-label">Meta</span>
                <span className="mp__ext-score-val">{ext.metascore}</span>
              </div>
            )}
          </div>

          {/* Meta şerit */}
          <div className="mp__meta-strip">
            {movie.year && <span className="mp__meta"><LuCalendar />{movie.year}</span>}
            {ext?.runtime && <span className="mp__meta"><LuClock />{ext.runtime} dk</span>}
            {ext?.country && <span className="mp__meta"><LuGlobe />{ext.country}</span>}
            {ext?.rated && <span className="mp__meta mp__meta--rated">{ext.rated}</span>}
          </div>

          {/* Türler */}
          <div className="mp__genres">
            {movie.genres.split("|").map((g) => (
              <span key={g} className="mp__genre">{g}</span>
            ))}
          </div>

          {/* Özet (TMDb > OMDb) */}
          {(ext?.overview || ext?.plot) && (
            <p className="mp__overview">{ext.overview || ext.plot}</p>
          )}

          {/* Yönetmen */}
          {ext?.director && (
            <div className="mp__director">
              <span className="mp__director-label">Yönetmen</span>
              <span className="mp__director-val">{ext.director}</span>
            </div>
          )}

          {/* Ödüller */}
          {ext?.awards && ext.awards !== "N/A" && (
            <div className="mp__awards">
              <LuAward /><span>{ext.awards}</span>
            </div>
          )}

          {/* Öneri nedeni */}
          {movie.reason && (
            <div className="mp__reason">
              <LuInfo /><span>{movie.reason}</span>
            </div>
          )}

          {/* Butonlar */}
          <div className="mp__actions">
            {localExtensions.map(({ MovieActions }, i) =>
              MovieActions ? <MovieActions key={i} movie={movie} /> : null)}
            {ext?.trailer_key && (
              <button className="mp__btn mp__btn--trailer" onClick={() => setShowTrailer(true)}>
                <LuPlay /> Fragman
              </button>
            )}
          </div>

          <RatingBars avg={movie.avg_rating} count={movie.rating_count} />

          {tags.length > 0 && (
            <div className="mp__section">
              <div className="mp__section-title">Etiketler</div>
              <div className="mp__tags">
                {tags.map((t) => <span key={t} className="mp__tag">{t}</span>)}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Oyuncu kadrosu */}
      {cast.length > 0 && (
        <div className="mp__cast-section page-container">
          <div className="mp__section-title mp__section-title--big">Oyuncu Kadrosu</div>
          <div className="mp__cast-viewport">
            <div className="mp__cast-scroll" ref={castScrollRef}
              onScroll={() => scrollState(castScrollRef, setCastLeft, setCastRight)}>
              {cast.map((m, i) => <CastCard key={i} member={m} />)}
            </div>
            {castLeft && (
              <button className="mp__cast-arrow mp__cast-arrow--prev"
                onClick={() => castScrollRef.current?.scrollBy({ left: -460, behavior: "smooth" })}>
                <LuChevronLeft />
              </button>
            )}
            {castRight && (
              <button className="mp__cast-arrow mp__cast-arrow--next"
                onClick={() => castScrollRef.current?.scrollBy({ left: 460, behavior: "smooth" })}>
                <LuChevronRight />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Benzer filmler */}
      {similar.length > 0 && (
        <div className="mp__similar-section page-container">
          <div className="mp__section-title mp__section-title--big">Benzer Filmler</div>
          <div className="mp__similar-viewport">
            <div className="mp__similar-scroll" ref={similarScrollRef}
              onScroll={() => scrollState(similarScrollRef, setSimLeft, setSimRight)}>
              {similar.map((m) => (
                <MovieCard key={m.movieId} movie={m}
                  onClick={(s) => navigate("/movie/" + s.movieId, { state: { movie: s } })} />
              ))}
            </div>
            {simLeft && (
              <button className="mp__similar-arrow mp__similar-arrow--prev"
                onClick={() => similarScrollRef.current?.scrollBy({ left: -600, behavior: "smooth" })}>
                <LuChevronLeft />
              </button>
            )}
            {simRight && (
              <button className="mp__similar-arrow mp__similar-arrow--next"
                onClick={() => similarScrollRef.current?.scrollBy({ left: 600, behavior: "smooth" })}>
                <LuChevronRight />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Fragman overlay */}
      {showTrailer && ext?.trailer_key && (
        <div className="mp__trailer-overlay" onClick={() => setShowTrailer(false)}>
          <div className="mp__trailer-panel" onClick={(e) => e.stopPropagation()}>
            <button className="mp__trailer-close" onClick={() => setShowTrailer(false)}>
              <LuX />
            </button>
            <iframe
              src={`https://www.youtube.com/embed/${ext.trailer_key}?autoplay=1`}
              allow="autoplay; fullscreen"
              allowFullScreen
              title={`${movie.title} fragman`}
            />
          </div>
        </div>
      )}
    </div>
  );
}
