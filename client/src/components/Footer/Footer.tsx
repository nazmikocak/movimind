import { useNavigate } from "react-router-dom";
import Logo from "../Logo/Logo";
import "./Footer.scss";

const NAV_LINKS = [
  { label: "Ana Sayfa", path: "/" },
  { label: "Veri Seti", path: "/dataset" },
  { label: "Öneriler", path: "/recommend" },
];

const INFO_LINKS = [
  "Gizlilik Politikası",
  "Kullanım Koşulları",
  "Çerez Tercihleri",
];

export default function Footer() {
  const navigate = useNavigate();
  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer__inner">
        {/* Üst satır: logo + nav + bilgi */}
        <div className="footer__top">
          <div className="footer__brand" onClick={() => navigate("/")}>
            <Logo size="md" className="footer__logo" />
          </div>

          <nav className="footer__nav">
            {NAV_LINKS.map((l) => (
              <button
                key={l.path}
                className="footer__nav-link"
                onClick={() => navigate(l.path)}
              >
                {l.label}
              </button>
            ))}
          </nav>

          <div className="footer__meta">
            <span className="footer__dataset">
              <a
                className="footer__dataset-link"
                href="https://grouplens.org/datasets/movielens/"
                target="_blank"
                rel="noopener noreferrer"
              >
                MovieLens
              </a>{" "}
              veri seti kullanılmıştır.
            </span>
            <span className="footer__dataset">
              Film bilgileri ve görseller{" "}
              <a
                className="footer__dataset-link"
                href="https://www.themoviedb.org/"
                target="_blank"
                rel="noopener noreferrer"
              >
                TMDB
              </a>
              , IMDb puanları{" "}
              <a
                className="footer__dataset-link"
                href="https://www.omdbapi.com/"
                target="_blank"
                rel="noopener noreferrer"
              >
                OMDb API
              </a>{" "}
              kaynaklıdır.
            </span>
            <span className="footer__dataset">
              Bu ürün TMDB API'sini kullanır ancak TMDB tarafından onaylanmış veya
              sertifikalandırılmış değildir.
            </span>
          </div>
        </div>

        {/* Ayraç */}
        <div className="footer__divider" />

        {/* Alt satır: telif + info linkleri */}
        <div className="footer__bottom">
          <span className="footer__copy">
            © {year} MOVIMIND, Tüm hakları saklıdır.{" "}
            <a
              className="footer__author"
              href="https://www.linkedin.com/in/nazmikocak/"
              target="_blank"
              rel="noopener noreferrer"
            >
              Nazmi Koçak
            </a>{" "}
            tarafından geliştirilmiştir.
          </span>
          <div className="footer__info-links">
            {INFO_LINKS.map((l) => (
              <span key={l} className="footer__info-link">{l}</span>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
