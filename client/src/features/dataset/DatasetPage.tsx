import { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
  AreaChart, Area, PieChart, Pie, Legend,
} from "recharts";
import {
  LuFilm, LuUsers, LuStar, LuActivity, LuChartBar, LuChartPie,
  LuChartLine, LuTrophy, LuFlame, LuBrain, LuTarget, LuGauge,
  LuLayers, LuPercent, LuBookOpen, LuExternalLink,
} from "react-icons/lu";
import type { AnalysisData } from "../../types/movie";
import { API } from "../../services/api";
import "./DatasetPage.scss";
import { useDocumentTitle } from "../../hooks/useDocumentTitle";

const fmt = (n: number) => n?.toLocaleString("tr-TR");
const RED = "#E50914";

const tooltipStyle = {
  background: "#1C1C1C",
  border: "1px solid #333",
  borderRadius: 8,
  color: "#FFFFFF",
  fontSize: 13,
  boxShadow: "0 8px 28px rgba(0,0,0,0.55)",
};
// Tooltip metni her zaman açık renk: seri rengi koyu zeminde okunmuyor
const tooltipItemStyle = { color: "#FFFFFF" };
const tooltipLabelStyle = { color: "#B3B3B3", fontWeight: 600, marginBottom: 4 };

function StatCard({ Icon, value, label }: { Icon: typeof LuFilm; value: string; label: string }) {
  return (
    <div className="dataset__stat-card">
      <div className="dataset__stat-card-icon"><Icon /></div>
      <div className="dataset__stat-card-value">{value || "—"}</div>
      <div className="dataset__stat-card-label">{label}</div>
    </div>
  );
}

function ChartCard({ Icon, title, children }: { Icon: typeof LuFilm; title: string; children: React.ReactNode }) {
  return (
    <div className="dataset__chart-card">
      <div className="dataset__chart-head">
        <span className="dataset__chart-icon"><Icon /></span>
        <span className="dataset__chart-title">{title}</span>
      </div>
      <div className="dataset__chart-body">{children}</div>
    </div>
  );
}

function MovieTable({ Icon, title, rows }: { Icon: typeof LuFilm; title: string; rows: AnalysisData["top_rated"] }) {
  return (
    <div className="dataset__section">
      <div className="dataset__section-head">
        <span className="dataset__section-icon"><Icon /></span>
        <span className="dataset__section-title">{title}</span>
      </div>
      <div className="dataset__table-wrap">
        <table className="dataset__table">
          <thead>
            <tr>
              <th className="rank">#</th><th>Film</th><th>Tür</th>
              <th>Yıl</th><th>Puan</th><th>Oy</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((f, i) => (
              <tr key={f.movieId}>
                <td className="rank">{i + 1}</td>
                <td>{f.title}</td>
                <td>{f.genres.replace(/\|/g, ", ")}</td>
                <td>{f.year ?? "—"}</td>
                <td className="rating"><LuStar /> {f.avg_rating}</td>
                <td className="count">{fmt(f.rating_count)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Bar2({ pct, label, sub }: { pct: number; label: string; sub: string }) {
  return (
    <div className="dataset__pbar">
      <div className="dataset__pbar-head">
        <span className="dataset__pbar-label">{label}</span>
        <span className="dataset__pbar-pct">%{pct.toFixed(1)}</span>
      </div>
      <div className="dataset__pbar-track">
        <div className="dataset__pbar-fill" style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <div className="dataset__pbar-sub">{sub}</div>
    </div>
  );
}

export default function DatasetPage() {
  useDocumentTitle("Veri Seti Analizi");
  const [data, setData] = useState<AnalysisData | null>(null);

  useEffect(() => {
    API.analysis().then(setData).catch(() => {});
  }, []);

  const stats = data?.stats;
  const model = data?.model;
  const d = data?.descriptive;
  const si = stats?.sample_info;

  const genreCount = data?.genre_distribution?.length ?? 0;

  const popularity = (data?.popularity_distribution ?? []).map((p) => ({
    name: p.bucket, value: p.count,
  }));
  const POP_COLORS = ["#5A0E1B", "#7A1F4B", "#B00710", "#E50914", "#FF3D47"];

  return (
    <div className="dataset page-container">
      <div className="dataset__header">
        <h1 className="dataset__page-title">Veri Seti Analizi</h1>
        <p className="dataset__page-sub">
          Önerilerin dayandığı veri setinin istatistikleri, dağılımları ve
          model başarımı.
        </p>
      </div>

      <div className="dataset__stat-grid">
        <StatCard Icon={LuFilm} value={fmt(stats?.total_movies ?? 0)} label="Film Sayısı" />
        <StatCard Icon={LuUsers} value={fmt(stats?.total_users ?? 0)} label="Kullanıcı Sayısı" />
        <StatCard Icon={LuStar} value={fmt(stats?.total_ratings ?? 0)} label="Puanlama Sayısı" />
        <StatCard Icon={LuActivity} value={String(stats?.avg_rating ?? "—")} label="Ortalama Puan" />
      </div>

      <div className="dataset__charts">
        <ChartCard Icon={LuChartBar} title="Tür Dağılımı (Film Sayısı)">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart
              data={data?.genre_distribution ?? []}
              layout="vertical"
              margin={{ left: 12, right: 16 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#262626" horizontal={false} />
              <XAxis type="number" stroke="#8C8C8C" fontSize={11} />
              <YAxis type="category" dataKey="genre" stroke="#8C8C8C" fontSize={11} width={78} />
              <Tooltip contentStyle={tooltipStyle} itemStyle={tooltipItemStyle} labelStyle={tooltipLabelStyle}
                cursor={{ fill: "rgba(229,9,20,0.08)" }}
                formatter={(v: number) => [fmt(v), "Film Sayısı"]} />
              <Bar dataKey="count" name="Film Sayısı" fill={RED} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard Icon={LuChartPie} title="Oy Sayısına Göre Film Dağılımı">
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={popularity}
                dataKey="value"
                nameKey="name"
                cx="50%" cy="50%"
                outerRadius={108}
                innerRadius={82}
                paddingAngle={2}
              >
                {popularity.map((_, i) => (
                  <Cell key={i} fill={POP_COLORS[i % POP_COLORS.length]} stroke="#0B0B0B" />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} itemStyle={tooltipItemStyle} labelStyle={tooltipLabelStyle}
                formatter={(v: number) => [fmt(v), "Film Sayısı"]} />
              <Legend wrapperStyle={{ fontSize: 11, color: "#8C8C8C" }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard Icon={LuStar} title="Puan Dağılımı (0.5 – 5.0)">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data?.rating_distribution ?? []} margin={{ left: 4, right: 12 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
              <XAxis dataKey="rating" stroke="#8C8C8C" fontSize={11} />
              <YAxis stroke="#8C8C8C" fontSize={11}
                tickFormatter={(v) => (v >= 1e6 ? `${(v / 1e6).toFixed(0)}M` : v >= 1e3 ? `${(v / 1e3).toFixed(0)}K` : `${v}`)} />
              <Tooltip contentStyle={tooltipStyle} itemStyle={tooltipItemStyle} labelStyle={tooltipLabelStyle}
                cursor={{ fill: "rgba(229,9,20,0.08)" }}
                labelFormatter={(v) => `Puan: ${v}`}
                formatter={(v: number) => [fmt(v), "Puanlama Sayısı"]} />
              <Bar dataKey="count" name="Puanlama Sayısı" radius={[4, 4, 0, 0]}>
                {(data?.rating_distribution ?? []).map((_, i) => (
                  <Cell key={i} fill={i >= (data?.rating_distribution.length ?? 0) - 3 ? RED : "#7A1F4B"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard Icon={LuChartLine} title="Yıllara Göre Film Sayısı">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data?.year_distribution ?? []} margin={{ left: 4, right: 12 }}>
              <defs>
                <linearGradient id="yearFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={RED} stopOpacity={0.7} />
                  <stop offset="100%" stopColor={RED} stopOpacity={0.04} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#262626" vertical={false} />
              <XAxis dataKey="year" stroke="#8C8C8C" fontSize={11} minTickGap={28} />
              <YAxis stroke="#8C8C8C" fontSize={11} />
              <Tooltip contentStyle={tooltipStyle} itemStyle={tooltipItemStyle} labelStyle={tooltipLabelStyle}
                cursor={{ stroke: RED }}
                labelFormatter={(v) => `Yıl: ${v}`}
                formatter={(v: number) => [fmt(v), "Film Sayısı"]} />
              <Area type="monotone" dataKey="count" name="Film Sayısı" stroke={RED} strokeWidth={2} fill="url(#yearFill)" />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {d && stats && (
        <div className="dataset__section">
          <div className="dataset__section-head">
            <span className="dataset__section-icon"><LuGauge /></span>
            <span className="dataset__section-title">Veri Seti İstatistikleri</span>
          </div>
          <div className="dataset__desc-grid">
            {[
              ["Film Sayısı", fmt(stats.total_movies)],
              ["Kategori Sayısı", fmt(genreCount)],
              ["Kullanıcı Sayısı", fmt(stats.total_users)],
              ["Puanlama Sayısı", fmt(stats.total_ratings)],
              ["Ortalama Puan", stats.avg_rating],
              ["Medyan Puan", d.median],
              ["Standart Sapma", d.std],
              ["Kullanıcı Başına Ort. Oy", d.ratings_per_user],
              ["Film Başına Ort. Oy", d.ratings_per_movie],
            ].map(([l, v]) => (
              <div key={l as string} className="dataset__desc-cell">
                <div className="dataset__desc-val">{v as React.ReactNode}</div>
                <div className="dataset__desc-label">{l as string}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {model && (
        <div className="dataset__section">
          <div className="dataset__section-head">
            <span className="dataset__section-icon"><LuBrain /></span>
            <span className="dataset__section-title">Model Performansı</span>
          </div>
          <div className="dataset__model-grid">
            <div className="dataset__model-card dataset__model-card--hl">
              <div className="dataset__model-ic"><LuTarget /></div>
              <div className="dataset__model-val">
                {model.precision != null ? `%${(model.precision * 100).toFixed(1)}` : "—"}
              </div>
              <div className="dataset__model-label">İsabet (Precision)</div>
            </div>
            <div className="dataset__model-card">
              <div className="dataset__model-ic"><LuGauge /></div>
              <div className="dataset__model-val">{model.rmse ?? "—"}</div>
              <div className="dataset__model-label">RMSE</div>
            </div>
            <div className="dataset__model-card">
              <div className="dataset__model-ic"><LuActivity /></div>
              <div className="dataset__model-val">{model.mae ?? "—"}</div>
              <div className="dataset__model-label">MAE</div>
            </div>
            <div className="dataset__model-card">
              <div className="dataset__model-ic"><LuLayers /></div>
              <div className="dataset__model-val">K={model.k}</div>
              <div className="dataset__model-label">Komşu Sayısı</div>
            </div>
            <div className="dataset__model-card">
              <div className="dataset__model-ic"><LuFilm /></div>
              <div className="dataset__model-val">{fmt(model.n_movies)}</div>
              <div className="dataset__model-label">Film (Matris Satırı)</div>
            </div>
            <div className="dataset__model-card">
              <div className="dataset__model-ic"><LuUsers /></div>
              <div className="dataset__model-val">{fmt(model.n_users)}</div>
              <div className="dataset__model-label">Kullanıcı (Boyut)</div>
            </div>
          </div>
        </div>
      )}

      {data && <MovieTable Icon={LuTrophy} title="En Yüksek Ortalama Puanlı 10 Film" rows={data.top_rated} />}
      {data && <MovieTable Icon={LuFlame} title="En Çok Puanlanan 10 Film" rows={data.most_rated} />}

      <div className="dataset__section">
        <div className="dataset__section-head">
          <span className="dataset__section-icon"><LuLayers /></span>
          <span className="dataset__section-title">Veri Temizleme ve Örneklem Optimizasyonu</span>
        </div>
        <div className="dataset__cleaning">
          <div className="dataset__cleaning-col dataset__cleaning-col--before">
            <div className="dataset__cleaning-col-title">Ham Veri Seti</div>
            {[
              ["Film Sayısı", fmt(si?.original_movies ?? 87585)],
              ["Kullanıcı Sayısı", fmt(si?.original_users ?? 200948)],
              ["Puanlama Sayısı", fmt(si?.original_ratings ?? 32000204)],
              ["Etiket Kayıtları", "2.000.072"],
            ].map(([l, v]) => (
              <div key={l} className="dataset__cleaning-row">
                <span className="dataset__cleaning-row-label">{l}</span>
                <span className="dataset__cleaning-row-value">{v}</span>
              </div>
            ))}
          </div>
          <div className="dataset__cleaning-col dataset__cleaning-col--after">
            <div className="dataset__cleaning-col-title">Temizlenmiş Veri Seti</div>
            {[
              ["Film Sayısı", fmt(si?.used_movies ?? 0)],
              ["Kullanıcı Sayısı", fmt(si?.used_users ?? 0)],
              ["Puanlama Sayısı", fmt(si?.used_ratings ?? 0)],
              ["Film Eşiği", `≥ ${si?.film_threshold ?? 75} oy`],
              ["Kullanıcı Eşiği", `≥ ${si?.user_threshold ?? 30} oy`],
            ].map(([l, v]) => (
              <div key={l} className="dataset__cleaning-row">
                <span className="dataset__cleaning-row-label">{l}</span>
                <span className="dataset__cleaning-row-value">{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {si && (
        <div className="dataset__section dataset__sample">
          <div className="dataset__section-head">
            <span className="dataset__section-icon"><LuPercent /></span>
            <span className="dataset__section-title">Ham Veri Setinden Alınan Örneklem Oranı</span>
          </div>
          <div className="dataset__sample-bars">
            <Bar2 pct={si.ratings_pct} label="Puanlama"
              sub={`${fmt(si.used_ratings)} / ${fmt(si.original_ratings)}`} />
            <Bar2 pct={si.movies_pct} label="Film"
              sub={`${fmt(si.used_movies)} / ${fmt(si.original_movies)}`} />
            <Bar2 pct={si.users_pct} label="Kullanıcı"
              sub={`${fmt(si.used_users)} / ${fmt(si.original_users)}`} />
          </div>
          <p className="dataset__sample-note">
            Gürültüyü azaltmak ve eğitimi hızlandırmak için ham veri setinin
            dengeli bir alt-örneklemi kullanıldı.
          </p>
        </div>
      )}

      <div className="dataset__section">
        <div className="dataset__section-head">
          <span className="dataset__section-icon"><LuBookOpen /></span>
          <span className="dataset__section-title">Veri Seti ve Atıf</span>
        </div>
        {/* MovieLens kullanım lisansı atıf istiyor */}
        <div className="dataset__cite">
          <p className="dataset__cite-text">
            Bu projede, Minnesota Üniversitesi <strong>GroupLens</strong> araştırma
            grubu tarafından sağlanan <strong>MovieLens 32M</strong> veri seti
            kullanılmıştır. Veri seti, 9 Ocak 1995 – 12 Ekim 2023 tarihleri arasında
            200.948 kullanıcının 87.585 filme verdiği 32.000.204 puanlama ile
            2.000.072 etiketi içerir. Veri seti yalnızca akademik amaçla kullanılmıştır.
          </p>
          <div className="dataset__cite-ref">
            F. Maxwell Harper ve Joseph A. Konstan. 2015. The MovieLens Datasets:
            History and Context. ACM Transactions on Interactive Intelligent Systems
            (TiiS) 5, 4: 19:1–19:19.
          </div>
          <div className="dataset__cite-links">
            <a className="dataset__cite-link" href="https://doi.org/10.1145/2827872"
              target="_blank" rel="noopener noreferrer">
              <LuExternalLink /> doi.org/10.1145/2827872
            </a>
            <a className="dataset__cite-link" href="https://grouplens.org/datasets/movielens/"
              target="_blank" rel="noopener noreferrer">
              <LuExternalLink /> grouplens.org/datasets/movielens
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
