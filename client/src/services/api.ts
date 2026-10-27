import type {
  Movie,
  DatasetStats,
  RecommendParams,
  AnalysisData,
  ModelInfo,
  MovieDetails,
} from "../types/movie";

// Yalnızca kendi server'ımız — başka hiçbir dış kaynak (madde 6)
const BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const API = {
  base: BASE,

  health: () => get<{ status: string; boot_id: string }>("/api/health"),

  stats: () => get<DatasetStats>("/api/stats"),

  modelInfo: () => get<ModelInfo>("/api/model-info"),

  analysis: () => get<AnalysisData>("/api/analysis"),

  topRated: (n = 10) => get<Movie[]>(`/api/top-rated?n=${n}`),

  mostRated: (n = 10) => get<Movie[]>(`/api/most-rated?n=${n}`),

  recommend: (params: RecommendParams) => {
    const clean: Record<string, string> = {};
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") clean[k] = String(v);
    });
    return get<Movie[]>(`/api/recommend?${new URLSearchParams(clean)}`);
  },

  search: (q: string, n = 10) =>
    get<Movie[]>(`/api/search?q=${encodeURIComponent(q)}&n=${n}`),

  similar: (movieId: number, n = 6) =>
    get<Movie[]>(`/api/similar/${movieId}?n=${n}`),

  movieDetails: (movieId: number) =>
    get<MovieDetails>(`/api/movie/${movieId}/details`),
};
