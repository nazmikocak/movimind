import { useNavigate } from "react-router-dom";
import { LuArrowRight } from "react-icons/lu";
import type { Movie } from "../../types/movie";
import { getPosterUrl } from "../../services/tmdb";
import "./PromoSection.scss";

interface Props {
  movie?: Movie;
  movies?: Movie[];
}

export default function PromoSection({ movie, movies = [] }: Props) {
  const navigate = useNavigate();

  const bgMovies = movies.length
    ? movies.slice(0, 18)
    : movie
      ? Array.from({ length: 3 }, () => movie)
      : [];

  return (
    <div className="promo">
      <div className="promo__bg" aria-hidden="true">
        {bgMovies.map((m, i) => {
          const url = m.imdbId ? getPosterUrl(m.imdbId) : null;
          return (
            <div
              key={i}
              className={`promo__bg-tile${!url ? " promo__bg-tile--empty" : ""}`}
              style={url ? { backgroundImage: `url(${url})` } : undefined}
            />
          );
        })}
        {bgMovies.length === 0 &&
          Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="promo__bg-tile promo__bg-tile--empty" />
          ))}
      </div>

      <div className="promo__overlay" />

      <div className="promo__content">
        <div className="promo__text">
          <h2 className="promo__title">
            Birbirinden Çeşitli Filmleri Keşfet
          </h2>
          <p className="promo__desc">
            Binlerce film arasından zevkine en uygun olanları saniyeler içinde
            keşfet. Beğenilerine en yakın yapımları senin için bir araya getiriyoruz.
          </p>
        </div>
        <button className="promo__btn" onClick={() => navigate("/recommend")}>
          Öneri Al <LuArrowRight />
        </button>
      </div>
    </div>
  );
}
