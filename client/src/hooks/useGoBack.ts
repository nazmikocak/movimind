import { useNavigate } from "react-router-dom";

/** Uygulama içinden gelindiyse bir önceki sayfaya, doğrudan linkle açıldıysa ana sayfaya döner. */
export function useGoBack() {
  const navigate = useNavigate();
  return () => {
    // React Router geçmişteki konumu history.state.idx'te tutar; 0 ise site içinde geri gidilecek sayfa yok
    const idx = (window.history.state as { idx?: number } | null)?.idx ?? 0;
    if (idx > 0) navigate(-1);
    else navigate("/");
  };
}
