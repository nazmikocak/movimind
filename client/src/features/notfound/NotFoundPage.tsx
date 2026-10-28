import { useNavigate } from "react-router-dom";
import { LuHouse, LuSparkles } from "react-icons/lu";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";
import "./NotFoundPage.scss";

interface Props {
  title?: string;
  message?: string;
}

export default function NotFoundPage({
  title = "Aradığın sayfa bulunamadı",
  message = "Bağlantı hatalı olabilir ya da sayfa kaldırılmış olabilir. Ana sayfaya dönebilir veya sana uygun filmleri keşfedebilirsin.",
}: Props) {
  const navigate = useNavigate();
  useDocumentTitle(title);

  return (
    <div className="not-found page-container">
      <div className="not-found__glow" aria-hidden="true" />
      <div className="not-found__code" aria-hidden="true">404</div>
      <h1 className="not-found__title">{title}</h1>
      <p className="not-found__text">{message}</p>
      <div className="not-found__actions">
        <button type="button" className="not-found__btn not-found__btn--primary" onClick={() => navigate("/")}>
          <LuHouse /> Ana Sayfa
        </button>
        <button type="button" className="not-found__btn" onClick={() => navigate("/recommend")}>
          <LuSparkles /> Öneri Al
        </button>
      </div>
    </div>
  );
}
