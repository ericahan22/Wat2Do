import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useApi } from "@/shared/hooks/useApi";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";

type ScanState = "loading" | "requesting-location" | "recorded" | "error";

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
  const [message, setMessage] = useState("Preparing your Wat2Do redirect...");

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
          setMessage("This poster is collecting its first scan location.");
          location = await getCurrentLocation();
        }

        const result = await posterAPIClient.recordPosterScan(
          posterId,
          location ?? {}
        );
        const destinationUrl = result.destination_url || "/events";

        setState("recorded");
        setMessage("Scan recorded. Redirecting you to Wat2Do...");

        window.setTimeout(() => {
          if (destinationUrl.startsWith("http")) {
            window.location.assign(destinationUrl);
          } else {
            navigate(destinationUrl, { replace: true });
          }
        }, 800);
      } catch {
        setState("error");
        setMessage("We couldn't record this scan, but you can still browse events.");
      }
    };

    void recordScan();
  }, [navigate, posterAPIClient, posterId]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <Card className="max-w-md w-full">
        <CardHeader>
          <CardTitle>
            {state === "error" ? "Scan Not Recorded" : "Wat2Do Poster Scan"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
          {state === "requesting-location" && (
            <p className="text-xs text-gray-500 dark:text-gray-500">
              Your browser may ask for permission. Only the first successful
              poster location is stored; later scans only increment the count.
            </p>
          )}
          {state === "error" && (
            <Button onClick={() => navigate("/events", { replace: true })}>
              Go to events
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default PosterScanPage;
