export interface Movie {
  movieId: number;
  title: string;
  genres: string;
  tags: string;
  year: number | null;
  avg_rating: number;
  rating_count: number;
  imdbId: string;
  tmdbId: number;
  poster_url?: string | null;
  distance?: number;
  reason?: string;
}

export interface SampleInfo {
  original_ratings: number;
  original_movies: number;
  original_users: number;
  used_ratings: number;
  used_movies: number;
  used_users: number;
  ratings_pct: number;
  movies_pct: number;
  users_pct: number;
  film_threshold: number;
  user_threshold: number;
}

export interface DatasetStats {
  total_users: number;
  total_movies: number;
  total_ratings: number;
  avg_rating: number;
  algorithm: string;
  dataset: string;
  sample_info: SampleInfo;
}

export interface RecommendParams {
  genre?: string;
  min_rating?: number;
  max_rating?: number;
  year_min?: number;
  year_max?: number;
  tag?: string;
  min_votes?: number;
  sort?: string;
  n?: number;
  movie_id?: number;
}

export interface ModelInfo {
  algorithm: string;
  k: number;
  n_movies: number;
  n_users: number;
  n_ratings?: number;
  rmse?: number | null;
  mae?: number | null;
  precision?: number | null;
  precision_k?: number;
  coverage?: number;
  n_eval?: number;
  centering?: string;
}

export interface AnalysisData {
  genre_distribution: { genre: string; count: number }[];
  rating_distribution: { rating: number; count: number }[];
  year_distribution: { year: number; count: number; avg_rating: number }[];
  popularity_distribution: { bucket: string; count: number }[];
  descriptive: {
    count: number;
    mean: number;
    median: number;
    std: number;
    min: number;
    max: number;
    q1: number;
    q3: number;
    ratings_per_user: number;
    ratings_per_movie: number;
  };
  top_rated: Movie[];
  most_rated: Movie[];
  stats: DatasetStats;
  model: ModelInfo;
}

export interface CastMember {
  name: string;
  character: string | null;
  photo: string | null;
}

export interface ExternalDetails {
  available: boolean;
  overview?: string | null;
  tagline?: string | null;
  runtime?: number | null;
  release_date?: string | null;
  poster?: string | null;
  backdrop?: string | null;
  tmdb_rating?: number | null;
  tmdb_votes?: number | null;
  budget?: number | null;
  revenue?: number | null;
  cast?: CastMember[];
  director?: string | null;
  trailer_key?: string | null;
  imdb_rating?: string | null;
  imdb_votes?: string | null;
  awards?: string | null;
  language?: string | null;
  country?: string | null;
  rated?: string | null;
  plot?: string | null;
  actors?: string | null;
  released?: string | null;
  metascore?: string | null;
}

export interface MovieDetails extends Movie {
  external: ExternalDetails;
}
