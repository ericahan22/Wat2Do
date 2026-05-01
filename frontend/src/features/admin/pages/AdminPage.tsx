import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import type { PosterCampaign, PosterScan } from "@/shared/api";
import { useApi } from "@/shared/hooks/useApi";
import { PosterScanMap } from "@/features/posters/components/PosterScanMap";
import { useClerk } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Sparkles, FileText, Activity, QrCode } from "lucide-react";

function isToday(timestamp: string) {
  const date = new Date(timestamp);
  const now = new Date();
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  );
}

function AdminPage() {
  const { signOut } = useClerk();
  const navigate = useNavigate();
  const { posterAPIClient } = useApi();
  const [posterLabel, setPosterLabel] = useState("");
  const [destinationUrl, setDestinationUrl] = useState("");
  const [generatedPoster, setGeneratedPoster] = useState<PosterCampaign | null>(null);
  const [posterCampaigns, setPosterCampaigns] = useState<PosterCampaign[]>([]);
  const [posterScans, setPosterScans] = useState<PosterScan[]>([]);
  const [isGeneratingPoster, setIsGeneratingPoster] = useState(false);
  const [isLoadingPosters, setIsLoadingPosters] = useState(false);
  const [posterError, setPosterError] = useState<string | null>(null);

  const refreshPosterCampaigns = useCallback(async () => {
    setIsLoadingPosters(true);
    try {
      const [campaignsResponse, scansResponse] = await Promise.all([
        posterAPIClient.listPosterCampaigns(),
        posterAPIClient.listPosterScans(),
      ]);
      setPosterCampaigns(campaignsResponse.posters);
      setPosterScans(scansResponse.scans);
    } catch (error) {
      console.error("Failed to load poster campaigns", error);
    } finally {
      setIsLoadingPosters(false);
    }
  }, [posterAPIClient]);

  useEffect(() => {
    void refreshPosterCampaigns();
  }, [refreshPosterCampaigns]);

  const handleLogout = () => {
    signOut();
  };

  const handleCreatePoster = async () => {
    const label = posterLabel.trim();
    if (!label) {
      setPosterError("Poster label is required.");
      return;
    }

    setIsGeneratingPoster(true);
    setPosterError(null);

    try {
      const poster = await posterAPIClient.createPosterCampaign({
        label,
        destination_url: destinationUrl.trim() || `${window.location.origin}/events`,
        base_url: window.location.origin,
      });
      setGeneratedPoster(poster);
      await refreshPosterCampaigns();
    } catch (error) {
      setPosterError(error instanceof Error ? error.message : "Failed to create poster QR code.");
    } finally {
      setIsGeneratingPoster(false);
    }
  };

  const todaysScans = useMemo(
    () => posterScans.filter((scan) => isToday(scan.created_at)),
    [posterScans]
  );

  const hourlyScanCounts = useMemo(() => {
    const counts = Array.from({ length: 24 }, (_, hour) => ({
      hour,
      label: `${hour.toString().padStart(2, "0")}:00`,
      count: 0,
    }));

    for (const scan of todaysScans) {
      counts[new Date(scan.created_at).getHours()].count += 1;
    }

    return counts;
  }, [todaysScans]);

  const maxHourlyScanCount = Math.max(
    ...hourlyScanCounts.map((bucket) => bucket.count),
    1
  );

  const totalScanCount = posterCampaigns.reduce(
    (total, poster) => total + poster.scan_count,
    0
  );

  const copyScanUrl = async () => {
    if (!generatedPoster) return;
    await navigator.clipboard.writeText(generatedPoster.scan_url);
  };

  const adminCards = [
    {
      title: "Event Promotions",
      description: "Manage event promotions and featured events",
      icon: Sparkles,
      route: "/admin/promotions",
      color: "text-purple-600 dark:text-purple-400",
    },
    {
      title: "Event Submissions",
      description: "Review and manage user-submitted events",
      icon: FileText,
      route: "/admin/submissions",
      color: "text-blue-600 dark:text-blue-400",
    },
    {
      title: "Scraping Diagnostics",
      description: "Monitor scraping pipeline and find missing posts",
      icon: Activity,
      route: "/admin/scraping",
      color: "text-orange-600 dark:text-orange-400",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <Button onClick={handleLogout} variant="destructive">
            Logout
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {adminCards.map((card) => {
            const Icon = card.icon;
            return (
              <Card
                key={card.route}
                className="cursor-pointer transition-all hover:shadow-lg hover:scale-105"
                onClick={() => navigate(card.route)}
              >
                <CardHeader>
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-lg bg-gray-100 dark:bg-gray-800 ${card.color}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <CardTitle className="text-xl">{card.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{card.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <Card className="mt-6">
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-gray-100 dark:bg-gray-800 text-green-600 dark:text-green-400">
                <QrCode className="h-6 w-6" />
              </div>
              <CardTitle className="text-xl">Poster QR Tracking</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Generate a QR code URL for a physical poster. The first scanner can
              save location coordinates; every scan increments the count.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="poster-label">
                  Poster label
                </label>
                <Input
                  id="poster-label"
                  value={posterLabel}
                  onChange={(event) => setPosterLabel(event.target.value)}
                  placeholder="UPenn Spring 2026 dining hall poster"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="destination-url">
                  Redirect after scan
                </label>
                <Input
                  id="destination-url"
                  value={destinationUrl}
                  onChange={(event) => setDestinationUrl(event.target.value)}
                  placeholder={`${window.location.origin}/events`}
                />
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button onClick={handleCreatePoster} disabled={isGeneratingPoster}>
                {isGeneratingPoster ? "Generating..." : "Generate QR code"}
              </Button>
              {generatedPoster && (
                <Button variant="outline" onClick={copyScanUrl}>
                  Copy scan URL
                </Button>
              )}
            </div>

            {posterError && (
              <p className="text-sm text-red-600 dark:text-red-400">{posterError}</p>
            )}

            {generatedPoster && (
              <div className="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-6 pt-2">
                <div
                  className="bg-white rounded-md border p-3 [&_svg]:h-full [&_svg]:w-full"
                  dangerouslySetInnerHTML={{ __html: generatedPoster.qr_svg }}
                />
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="font-medium">Poster ID:</span>{" "}
                    <code>{generatedPoster.id}</code>
                  </p>
                  <p>
                    <span className="font-medium">Scan URL:</span>{" "}
                    <a
                      className="text-blue-600 underline break-all"
                      href={generatedPoster.scan_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {generatedPoster.scan_url}
                    </a>
                  </p>
                  <p>
                    <span className="font-medium">Scans:</span>{" "}
                    {generatedPoster.scan_count}
                  </p>
                </div>
              </div>
            )}

            <div className="space-y-3 border-t border-gray-200 pt-4 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-semibold">Scan map</h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    Markers use poster first-scan coordinates and today's scan count.
                    Individual scan rows do not store coordinates.
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => void refreshPosterCampaigns()}
                  disabled={isLoadingPosters}
                >
                  {isLoadingPosters ? "Refreshing..." : "Refresh"}
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="rounded-md border border-gray-200 p-3 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Scans today</p>
                  <p className="text-2xl font-semibold">{todaysScans.length}</p>
                </div>
                <div className="rounded-md border border-gray-200 p-3 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Total scans</p>
                  <p className="text-2xl font-semibold">{totalScanCount}</p>
                </div>
                <div className="rounded-md border border-gray-200 p-3 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Located posters</p>
                  <p className="text-2xl font-semibold">
                    {
                      posterCampaigns.filter(
                        (poster) =>
                          poster.first_location.latitude != null &&
                          poster.first_location.longitude != null
                      ).length
                    }
                  </p>
                </div>
              </div>
              <PosterScanMap posters={posterCampaigns} scans={todaysScans} />
              <div className="rounded-md border border-gray-200 p-4 dark:border-gray-700">
                <div className="mb-3 flex items-center justify-between">
                  <h4 className="text-sm font-semibold">Scans throughout today</h4>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {todaysScans.length} scan{todaysScans.length === 1 ? "" : "s"}
                  </span>
                </div>
                <div className="flex h-28 items-end gap-1">
                  {hourlyScanCounts.map((bucket) => (
                    <div
                      key={bucket.hour}
                      className="flex min-w-0 flex-1 flex-col items-center gap-1"
                      title={`${bucket.label}: ${bucket.count} scans`}
                    >
                      <div className="flex h-20 w-full items-end rounded-sm bg-gray-100 dark:bg-gray-800">
                        <div
                          className="w-full rounded-sm bg-blue-600 transition-all"
                          style={{
                            height: `${Math.max(
                              bucket.count === 0 ? 0 : 8,
                              (bucket.count / maxHourlyScanCount) * 100
                            )}%`,
                          }}
                        />
                      </div>
                      {bucket.hour % 4 === 0 && (
                        <span className="text-[10px] text-gray-500 dark:text-gray-400">
                          {bucket.hour}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default AdminPage;
