import { useState } from 'react';
import type { Movie } from '../types/movie';
import { getPosterUrl, posterGradient } from '../services/tmdb';

/** Kart posteri: server'ın verdiği TMDb adresi; yüklenemezse türe göre gradyan. */
export function usePoster(movie: Pick<Movie, 'genres' | 'poster_url'> | null) {
  const url = movie ? getPosterUrl(movie) : null;
  const [hasError, setHasError] = useState(false);

  return {
    url:      hasError ? null : url,
    gradient: posterGradient(movie?.genres ?? 'Drama'),
    onError:  () => setHasError(true),
  };
}
