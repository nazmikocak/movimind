import { useEffect } from "react";
import {
  LuSwords,
  LuLaugh,
  LuClapperboard,
  LuGhost,
  LuRocket,
  LuHeart,
  LuZap,
  LuSparkles,
  LuCompass,
  LuShield,
  LuWand,
  LuFileText,
  LuX,
} from "react-icons/lu";
import type { IconType } from "react-icons";
import { setPreference } from "../../services/preferences";
import "./TonightModal.scss";

interface GenreOption {
  key: string;  // backend tür anahtarı (Action, Comedy ...)
  label: string;  // arayüzde gösterilen Türkçe ad
  Icon: IconType;
}

const OPTIONS: GenreOption[] = [
  { key: "Action", label: "Aksiyon", Icon: LuSwords },
  { key: "Comedy", label: "Komedi", Icon: LuLaugh },
  { key: "Drama", label: "Dram", Icon: LuClapperboard },
  { key: "Horror", label: "Korku", Icon: LuGhost },
  { key: "Sci-Fi", label: "Bilim Kurgu", Icon: LuRocket },
  { key: "Romance", label: "Romantik", Icon: LuHeart },
  { key: "Thriller", label: "Gerilim", Icon: LuZap },
  { key: "Animation", label: "Animasyon", Icon: LuSparkles },
  { key: "Adventure", label: "Macera", Icon: LuCompass },
  { key: "Crime", label: "Suç", Icon: LuShield },
  { key: "Fantasy", label: "Fantastik", Icon: LuWand },
  { key: "Documentary", label: "Belgesel", Icon: LuFileText },
];

interface Props {
  onClose: () => void;
  onSelect: (genre: string) => void;
}

export default function TonightModal({ onClose, onSelect }: Props) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && handleSkip();
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSkip = () => {
    onClose();
  };

  const handlePick = (genre: string) => {
    setPreference(genre);
    onSelect(genre);
    onClose();
  };

  return (
    <div className="tonight" onClick={handleSkip}>
      <div className="tonight__panel" onClick={(e) => e.stopPropagation()}>
        <button className="tonight__close" onClick={handleSkip} aria-label="Kapat">
          <LuX />
        </button>

        <div className="tonight__head">
          <span className="tonight__eyebrow">MOVIMIND</span>
          <h2 className="tonight__title">Bugün ne izlemek istersin?</h2>
          <p className="tonight__sub">
            Bir tür seç; KNN modeli bu akşam için sana özel öneriler hazırlasın.
          </p>
        </div>

        <div className="tonight__grid">
          {OPTIONS.map(({ key, label, Icon }) => (
            <button
              key={key}
              className="tonight__card"
              onClick={() => handlePick(key)}
            >
              <span className="tonight__card-icon">
                <Icon />
              </span>
              <span className="tonight__card-label">{label}</span>
            </button>
          ))}
        </div>

        <button className="tonight__skip" onClick={handleSkip}>
          Şimdilik geç
        </button>
      </div>
    </div>
  );
}
