import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import type { PosterCampaign } from "@/shared/api";
import { useApi } from "@/shared/hooks/useApi";
import { useClerk } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { Sparkles, FileText, Activity, QrCode } from "lucide-react";

function AdminPage() {
  const { signOut } = useClerk();
  const navigate = useNavigate();
  const { posterAPIClient } = useApi();
  const [posterLabel, setPosterLabel] = useState("");
  const [destinationUrl, setDestinationUrl] = useState("");
  const [generatedPoster, setGeneratedPoster] = useState<PosterCampaign | null>(null);
  const [isGeneratingPoster, setIsGeneratingPoster] = useState(false);
  const [posterError, setPosterError] = useState<string | null>(null);

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
    } catch (error) {
      setPosterError(error instanceof Error ? error.message : "Failed to create poster QR code.");
    } finally {
      setIsGeneratingPoster(false);
    }
  };

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
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default AdminPage;
