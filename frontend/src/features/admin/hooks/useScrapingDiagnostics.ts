import { useQuery } from "@tanstack/react-query";
import { useApi } from "@/shared/hooks/useApi";

export function useScrapingDiagnostics() {
  const { adminAPIClient } = useApi();

  const logsQuery = useQuery({
    queryKey: ["admin", "scraping", "logs"],
    queryFn: () => adminAPIClient.getAutomateLogs({ limit: 50, days: 7 }),
  });

  const runsQuery = useQuery({
    queryKey: ["admin", "scraping", "runs"],
    queryFn: () => adminAPIClient.getScrapeRuns({ limit: 50, days: 7 }),
  });

  const gapsQuery = useQuery({
    queryKey: ["admin", "scraping", "gaps"],
    queryFn: () => adminAPIClient.getGapAnalysis(),
  });

  return {
    logs: logsQuery.data,
    logsLoading: logsQuery.isLoading,
    runs: runsQuery.data,
    runsLoading: runsQuery.isLoading,
    gaps: gapsQuery.data,
    gapsLoading: gapsQuery.isLoading,
  };
}
