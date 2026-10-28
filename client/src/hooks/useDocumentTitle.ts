import { useEffect } from "react";

const SITE = "MOVIMIND";

/** Sekme başlığını "Başlık | MOVIMIND" yapar. */
export function useDocumentTitle(title: string) {
  useEffect(() => {
    document.title = `${title} | ${SITE}`;
  }, [title]);
}
