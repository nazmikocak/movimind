import { useNavigate, useLocation } from "react-router-dom";
import Logo from "../Logo/Logo";
import tmdbLogo from "../../assets/tmdb-logo.svg";
import "./Footer.scss";

const NAV_LINKS = [
  { label: "Ana Sayfa", path: "/" },
  { label: "Veri Seti", path: "/dataset" },
  { label: "Öneriler", path: "/recommend" },
];

const INFO_LINKS = ["Gizlilik Politikası", "Kullanım Koşulları", "Çerez Tercihleri"];

export default function Footer() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const year = new Date().getFullYear();

  const goTo = (path: string) => {
    if (pathname === path) window.scrollTo({ top: 0, behavior: "smooth" });
    else navigate(path);
  };

  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__top">
          <div className="footer__brand" onClick={() => goTo("/")}>
            <Logo size="md" className="footer__logo" />
          </div>

          <nav className="footer__nav">
            {NAV_LINKS.map((l) => (
              <button
                key={l.path}
                className="footer__nav-link"
                onClick={() => goTo(l.path)}
              >
                {l.label}
              </button>
            ))}
          </nav>

          <div className="footer__meta">
            {/* TMDB kullanım koşulu: logo ve bu uyarı metni zorunlu */}
            <span className="footer__dataset">
              <img className="footer__tmdb-logo" src={tmdbLogo} alt="" />
              Film bilgileri TMDB ve OMDb API'den alınır. Bu ürün TMDB API'sini
              kullanır; TMDB tarafından onaylanmış veya sertifikalandırılmış değildir.
            </span>
          </div>
        </div>

        <div className="footer__divider" />

        <div className="footer__bottom">
          <span className="footer__copy">
            © {year} MOVIMIND. Tüm hakları saklıdır.{" "}
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
