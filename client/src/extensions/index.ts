import type { ComponentType } from "react";
import type { Movie } from "../types/movie";

// Yalnızca yerelde bulunan eklentiler için bağlantı noktaları.
// `./local/` klasörü .gitignore'dadır; depoda ve canlı build'de liste boştur.
export interface LocalExtension {
  MovieActions?: ComponentType<{ movie: Movie }>;
  HomeRows?: ComponentType;
}

const modules = import.meta.glob<LocalExtension>("./local/*.extension.tsx", {
  eager: true,
  import: "default",
});

export const localExtensions: LocalExtension[] = Object.values(modules);
