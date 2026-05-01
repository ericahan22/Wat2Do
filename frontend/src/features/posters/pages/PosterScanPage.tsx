import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useApi } from "@/shared/hooks/useApi";

type ScanState = "loading" | "requesting-location" | "recorded";

interface LocationResult {
  latitude: number;
  longitude: number;
  accuracy_m?: number;
}

function getCurrentLocation(): Promise<LocationResult | null> {
  if (!navigator.geolocation) {
    return Promise.resolve(null);
  }

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy_m: position.coords.accuracy,
        });
      },
      () => resolve(null),
      {
        enableHighAccuracy: true,
        timeout: 8000,
        maximumAge: 0,
      }
    );
  });
}

export function PosterScanPage() {
  const { posterId: posterIdParam } = useParams<{ posterId: string }>();
  const [searchParams] = useSearchParams();
  const posterId = posterIdParam || searchParams.get("posterid") || undefined;
  const navigate = useNavigate();
  const { posterAPIClient } = useApi();
  const hasRecordedRef = useRef(false);
  const [state, setState] = useState<ScanState>("loading");

  useEffect(() => {
    if (!posterId || hasRecordedRef.current) {
      return;
    }

    hasRecordedRef.current = true;

    const recordScan = async () => {
      try {
        const status = await posterAPIClient.getPosterScanStatus(posterId);
        let location: LocationResult | null = null;

        if (status.needs_location) {
          setState("requesting-location");
          location = await getCurrentLocation();
        }

        const result = await posterAPIClient.recordPosterScan(
          posterId,
          location ?? {}
        );
        const destinationUrl = result.destination_url || "/events";

        setState("recorded");

        window.setTimeout(() => {
          if (destinationUrl.startsWith("http")) {
            window.location.assign(destinationUrl);
          } else {
            navigate(destinationUrl, { replace: true });
          }
        }, 800);
      } catch {
        navigate("/events", { replace: true });
      }
    };

    void recordScan();
  }, [navigate, posterAPIClient, posterId]);

  return <div className="min-h-[60vh]" aria-hidden="true" data-scan-state={state} />;
}

export default PosterScanPage;
