import { useState } from "react";
import { LuChevronDown } from "react-icons/lu";
import "./FaqSection.scss";

interface FaqItem {
  q: string;
  a: string;
}

const FAQ: FaqItem[] = [
  {
    q: "MOVIMIND nedir?",
    a: "MOVIMIND, beğenilerine en yakın filmleri keşfetmeni sağlayan kişisel bir film öneri platformudur. Amacımız, izlemek istediğin bir sonraki yapımı saniyeler içinde bulmana yardımcı olmaktır.",
  },
  {
    q: "Film önerileri nasıl oluşturuluyor?",
    a: "Öneriler, seçtiğin kriterlere ve senin zevkine benzer izleyicilerin tercihlerine göre oluşturulur. Tür, yıl, puan gibi filtrelerle sonuçları kendine göre şekillendirebilirsin.",
  },
  {
    q: "Önerileri nasıl alırım?",
    a: "Öneriler sayfasına git, ilgilendiğin türleri ve diğer kriterleri seç, ardından \"Öneri Al\" butonuna bas. Beğendiğin bir filmi yazarak ona benzer yapımları da bulabilirsin.",
  },
  {
    q: "Hangi veri seti kullanılıyor?",
    a: "Öneriler, akademik bir kaynak olan MovieLens film veri setine dayanır. Veri setinin istatistiklerini ve dağılımlarını Veri Seti sayfasında inceleyebilirsin.",
  },
  {
    q: "Filmleri MOVIMIND üzerinden izleyebilir miyim?",
    a: "Hayır. MOVIMIND bir öneri platformudur; film yayını yapmaz. Film detay sayfasında resmi fragmanı izleyebilir, oyuncu kadrosu ve puanlar gibi bilgilere ulaşabilirsin.",
  },
  {
    q: "Öneri algoritması nasıl çalışır?",
    a: "MOVIMIND, kullanıcı-tabanlı işbirlikçi filtreleme (collaborative filtering) yaklaşımını benimser. Her film, onu puanlayan kullanıcıların tercihlerine göre temsil edilir. Seçtiğin kriterlere uyan filmler, benzer izleyici profillerine sahip kullanıcıların en çok tercih ettiği yapımlar arasından sıralanır. Öneriler anlık hesaplanır; kişisel bir hesap veya geçmiş izleme kaydı gerektirmez.",
  },
  {
    q: "MOVIMIND ücretsiz mi?",
    a: "Evet. MOVIMIND bir dönem projesi olarak geliştirilmiştir ve tamamen ücretsizdir.",
  },
];

export default function FaqSection() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section className="faq">
      <div className="faq__head">
        <h2 className="faq__title">Sıkça Sorulan Sorular</h2>
        <p className="faq__sub">Merak ettiklerin için kısa yanıtlar.</p>
      </div>

      <div className="faq__list">
        {FAQ.map((item, i) => {
          const isOpen = open === i;
          return (
            <div key={i} className={`faq__item${isOpen ? " faq__item--open" : ""}`}>
              <button
                className="faq__question"
                onClick={() => setOpen(isOpen ? null : i)}
                aria-expanded={isOpen}
              >
                <span>{item.q}</span>
                <LuChevronDown className="faq__chevron" />
              </button>
              <div className="faq__answer">
                <p>{item.a}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
