import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import type { Movie } from "../../types/movie";
import { API } from "../../services/api";
import { getPosterUrl } from "../../services/tmdb";
import { shouldShowModal, markModalShown, getPreference } from "../../services/preferences";
import MovieRow from "../../components/MovieRow/MovieRow";
import PromoSection from "../../components/PromoSection/PromoSection";
import YearPicksSection from "../../components/YearPicksSection/YearPicksSection";
import GenreGrid from "../../components/GenreGrid/GenreGrid";
import TonightModal from "../../components/TonightModal/TonightModal";
import FaqSection from "../../components/FaqSection/FaqSection";
import { localExtensions } from "../../extensions";
import "./HomePage.scss";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";

// Backend tür anahtarı -> Türkçe ad ("Bu Gece İçin" başlığında)
const GENRE_TR: Record<string, string> = {
  Action: "Aksiyon", Comedy: "Komedi", Drama: "Dram", Horror: "Korku",
  "Sci-Fi": "Bilim Kurgu", Romance: "Romantik", Thriller: "Gerilim",
  Animation: "Animasyon", Adventure: "Macera", Crime: "Suç",
  Fantasy: "Fantastik", Documentary: "Belgesel",
};

export default function HomePage() {
  useDocumentTitle("Ana Sayfa");
  const navigate = useNavigate();
  const [topRated, setTopRated] = useState<Movie[]>([]);
  const [mostRated, setMostRated] = useState<Movie[]>([]);
  const [yearPicks, setYearPicks] = useState<Movie[]>([]);

  const [showModal, setShowModal] = useState(false);
  const [prefGenre, setPrefGenre] = useState<string | null>(
    getPreference()?.genre ?? null,
  );
  const [tonight, setTonight] = useState<Movie[]>([]);
  const [forYou, setForYou] = useState<Movie[]>([]);

  useEffect(() => {
    API.topRated(28).then(setTopRated).catch(() => {});
    API.mostRated(28).then(setMostRated).catch(() => {});
    API.recommend({ year_min: 2015, year_max: 2024, min_rating: 3.8, min_votes: 500, n: 5 })
      .then(setYearPicks)
      .catch(() => {});

    // Modal günde bir kez; server yeniden başladıysa her açılışta
    API.health().then(({ boot_id }) => {
      if (shouldShowModal(boot_id)) {
        setShowModal(true);
        markModalShown(boot_id);
      }
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!prefGenre) {
      setTonight([]);
      setForYou([]);
      return;
    }
    API.recommend({ genre: prefGenre, sort: "rating", min_votes: 300, n: 16 })
      .then(setTonight)
      .catch(() => {});
    API.recommend({ genre: prefGenre, sort: "popularity", min_votes: 300, n: 16 })
      .then(setForYou)
      .catch(() => {});
  }, [prefGenre]);

  const goToMovie = (m: Movie) =>
    navigate("/movie/" + m.movieId, { state: { movie: m } });

  const heroMovies = [...topRated, ...mostRated]
    .filter((m, idx, arr) => arr.findIndex((x) => x.movieId === m.movieId) === idx)
    .slice(0, 48);

  const heroTiles: Movie[] = heroMovies.length
    ? heroMovies
    : Array.from({ length: 48 }, (_, i): Movie => ({
        movieId: -1 - i, title: "", genres: "", tags: "", year: null,
        avg_rating: 0, rating_count: 0, imdbId: "", tmdbId: 0,
      }));

  const prefLabel = prefGenre ? GENRE_TR[prefGenre] ?? prefGenre : "";

  return (
    <div className="home">
      {showModal && (
        <TonightModal
          onClose={() => setShowModal(false)}
          onSelect={(g) => setPrefGenre(g)}
        />
      )}

      <div className="home__hero">
        <div className="home__hero-glow" />
        <div className="home__hero-collage" aria-hidden="true">
          {heroTiles.map((movie, i) => {
            const poster = getPosterUrl(movie);
            const tileStyle = poster ? { backgroundImage: `url(${poster})` } : undefined;
            return (
              <div
                key={`${movie.movieId}-${i}`}
                className={`home__hero-collage-tile home__hero-collage-tile--r${i % 4}`}
                style={tileStyle}
              />
            );
          })}
        </div>
        <div className="home__hero-inner">
          <div className="home__hero-content">
            <h1 className="home__hero-title">
              Sana Özel
              <br />
              <span>Film Önerileri</span>
            </h1>
            <p className="home__hero-sub">
              Zevkine en yakın filmleri keşfet, izlemek istediğin bir sonraki
              yapımı saniyeler içinde bul.
            </p>
            <div className="home__hero-actions">
              <button
                className="home__hero-btn home__hero-btn--primary"
                onClick={() => navigate("/recommend")}
              >
                Beğenilerine Özel Filmler Keşfet
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="home__rows">
        {localExtensions.map(({ HomeRows }, i) => (HomeRows ? <HomeRows key={i} /> : null))}
        <MovieRow title="En Yüksek Puanlı" movies={topRated} onMovieClick={goToMovie} />
        <MovieRow title="En Popüler" movies={mostRated} onMovieClick={goToMovie} />
        <YearPicksSection movies={yearPicks} />
        <GenreGrid />

        {tonight.length > 0 && (
          <MovieRow
            title={`Bu Gece İçin · ${prefLabel}`}
            movies={tonight}
            onMovieClick={goToMovie}
          />
        )}
        {forYou.length > 0 && (
          <MovieRow title="Sizin İçin" movies={forYou} onMovieClick={goToMovie} />
        )}

        <PromoSection movies={mostRated} />

        <FaqSection />
      </div>
    </div>
  );
}
