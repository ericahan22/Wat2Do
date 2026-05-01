import { useMemo, useState } from "react";
import MapboxMap, { Marker } from "react-map-gl/mapbox";
import "mapbox-gl/dist/mapbox-gl.css";
import { MapPin, Zap } from "lucide-react";
import type { PosterCampaign, PosterScan } from "@/shared/api";

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;
const EMPTY_SCANS: PosterScan[] = [];

interface PosterScanMapProps {
  posters: PosterCampaign[];
  scans?: PosterScan[];
  height?: string;
}

interface PosterLocation {
  id: string;
  label: string;
  scanCount: number;
  latitude: number;
  longitude: number;
}

function getMarkerColor(scanCount: number, maxScanCount: number) {
  if (maxScanCount <= 0) return "#0056D6";

  const ratio = scanCount / maxScanCount;
  if (ratio < 0.33) return "#22c55e";
  if (ratio < 0.67) return "#f59e0b";
  return "#ef4444";
}

function PosterMarker({
  poster,
  maxScanCount,
}: {
  poster: PosterLocation;
  maxScanCount: number;
}) {
  const [isHovered, setIsHovered] = useState(false);
  const color = getMarkerColor(poster.scanCount, maxScanCount);
  const size = Math.max(18, Math.min(34, 18 + (poster.scanCount / maxScanCount) * 16));

  return (
    <div
      className="relative cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div
        className="absolute rounded-full animate-ping"
        style={{
          width: size + 10,
          height: size + 10,
          backgroundColor: color,
          opacity: 0.16,
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
        }}
      />
      <div
        className="relative rounded-full border-2 border-white shadow-lg flex items-center justify-center text-[10px] font-bold text-white"
        style={{
          width: size,
          height: size,
          backgroundColor: color,
          textShadow: "0 1px 2px rgba(0,0,0,0.35)",
        }}
      >
        {poster.scanCount > 99 ? "99+" : poster.scanCount}
      </div>

      {isHovered && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 min-w-[180px] rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs shadow-xl dark:border-gray-700 dark:bg-gray-900">
          <div className="flex items-center gap-1.5 font-semibold">
            <MapPin className="h-3 w-3 text-blue-600" />
            <span className="truncate">{poster.label}</span>
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
            <Zap className="h-3 w-3" />
            <span>
              {poster.scanCount} scan{poster.scanCount === 1 ? "" : "s"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export function PosterScanMap({ posters, scans, height = "420px" }: PosterScanMapProps) {
  const visibleScans = scans ?? EMPTY_SCANS;
  const hasScanFilter = scans !== undefined;
  const scanCountByPoster = useMemo(() => {
    const counts = new Map<string, number>();
    for (const scan of visibleScans) {
      counts.set(scan.poster_id, (counts.get(scan.poster_id) ?? 0) + 1);
    }
    return counts;
  }, [visibleScans]);

  const posterLocations = useMemo(
    () =>
      posters
        .map((poster) => {
          const { latitude, longitude } = poster.first_location;
          if (latitude == null || longitude == null) return null;
          return {
            id: poster.id,
            label: poster.label,
            scanCount: hasScanFilter ? scanCountByPoster.get(poster.id) ?? 0 : poster.scan_count,
            latitude,
            longitude,
          };
        })
        .filter((poster): poster is PosterLocation => poster !== null),
    [hasScanFilter, posters, scanCountByPoster]
  );

  const maxScanCount = useMemo(
    () => Math.max(...posterLocations.map((poster) => poster.scanCount), 1),
    [posterLocations]
  );

  const center = useMemo(() => {
    if (posterLocations.length === 0) {
      return { latitude: 43.4723, longitude: -80.5449 };
    }

    return {
      latitude:
        posterLocations.reduce((sum, poster) => sum + poster.latitude, 0) /
        posterLocations.length,
      longitude:
        posterLocations.reduce((sum, poster) => sum + poster.longitude, 0) /
        posterLocations.length,
    };
  }, [posterLocations]);

  if (!MAPBOX_TOKEN) {
    return (
      <div
        className="flex items-center justify-center rounded-md border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900"
        style={{ height }}
      >
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Set VITE_MAPBOX_TOKEN to show the poster scan map.
        </p>
      </div>
    );
  }

  return (
    <div
      className="relative overflow-hidden rounded-md border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-900"
      style={{ height }}
    >
      <div className="absolute left-4 right-4 top-4 z-10 flex items-center justify-between rounded-lg border border-white/50 bg-white/90 px-3 py-2 text-xs shadow-sm backdrop-blur dark:border-gray-700/60 dark:bg-gray-900/90">
        <span className="font-medium">
          {posterLocations.length} located poster
          {posterLocations.length === 1 ? "" : "s"} •{" "}
          {posterLocations.reduce((sum, poster) => sum + poster.scanCount, 0)} shown scans
        </span>
        <span className="text-gray-600 dark:text-gray-400">
          First scan locations only
        </span>
      </div>

      <MapboxMap
        mapboxAccessToken={MAPBOX_TOKEN}
        initialViewState={{
          longitude: center.longitude,
          latitude: center.latitude,
          zoom: posterLocations.length > 0 ? 13 : 11,
        }}
        mapStyle="mapbox://styles/mapbox/light-v11"
        attributionControl={false}
        style={{ width: "100%", height: "100%" }}
      >
        {posterLocations.map((poster) => (
          <Marker
            key={poster.id}
            longitude={poster.longitude}
            latitude={poster.latitude}
            anchor="center"
          >
            <PosterMarker poster={poster} maxScanCount={maxScanCount} />
          </Marker>
        ))}
      </MapboxMap>
    </div>
  );
}

export default PosterScanMap;
