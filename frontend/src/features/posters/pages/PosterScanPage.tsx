import { useEffect } from "react";
import { useParams, useSearchParams } from "react-router-dom";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api").replace(
  /\/$/,
  ""
);

export function PosterScanPage() {
  const { posterId: posterIdParam } = useParams<{ posterId: string }>();
  const [searchParams] = useSearchParams();
  const posterId = posterIdParam || searchParams.get("posterid") || undefined;

  useEffect(() => {
    if (!posterId) {
      window.location.replace("/events");
      return;
    }

    window.location.replace(`${API_BASE_URL}/posters/${posterId}/redirect/`);
  }, [posterId]);

  return null;
}

export default PosterScanPage;
