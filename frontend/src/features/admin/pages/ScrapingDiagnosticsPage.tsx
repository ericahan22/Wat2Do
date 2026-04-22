import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { Loading } from "@/shared/components/ui/loading";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, AlertTriangle } from "lucide-react";
import { useScrapingDiagnostics } from "@/features/admin/hooks/useScrapingDiagnostics";
import type { ScrapeRun, AutomateLog, GapAccount } from "@/features/admin/types/scraping";

function StatusBadge({ value }: { value: string }) {
  const variant =
    value === "success" || value === "active"
      ? "default"
      : value === "error"
        ? "destructive"
        : "secondary";
  return <Badge variant={variant}>{value}</Badge>;
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleString();
}

function NotificationLogsTable({ logs }: { logs: AutomateLog[] }) {
  if (logs.length === 0) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">No logs in the last 7 days.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700 text-left text-gray-600 dark:text-gray-300">
            <th className="p-2 whitespace-nowrap">Time</th>
            <th className="p-2 whitespace-nowrap">Username</th>
            <th className="p-2 whitespace-nowrap">Resolved</th>
            <th className="p-2 whitespace-nowrap">Dispatched</th>
            <th className="p-2 whitespace-nowrap">Error</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="border-b border-gray-200 dark:border-gray-700">
              <td className="p-2 whitespace-nowrap">{formatDate(log.created_at)}</td>
              <td className="p-2">{log.ig_username || log.ig_user_id || "—"}</td>
              <td className="p-2">
                <Badge variant={log.username_resolved ? "default" : "destructive"}>
                  {log.username_resolved ? "yes" : "no"}
                </Badge>
              </td>
              <td className="p-2">
                <Badge variant={log.dispatch_sent ? "default" : "secondary"}>
                  {log.dispatch_sent ? "yes" : "no"}
                </Badge>
              </td>
              <td className="p-2 text-red-500 text-xs">{log.error_message || ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ScrapeRunsTable({ runs }: { runs: ScrapeRun[] }) {
  if (runs.length === 0) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">No scrape runs in the last 7 days.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700 text-left text-gray-600 dark:text-gray-300">
            <th className="p-2 whitespace-nowrap">Time</th>
            <th className="p-2 whitespace-nowrap">Username</th>
            <th className="p-2 whitespace-nowrap">Status</th>
            <th className="p-2 whitespace-nowrap">Fetched</th>
            <th className="p-2 whitespace-nowrap">New</th>
            <th className="p-2 whitespace-nowrap">Extracted</th>
            <th className="p-2 whitespace-nowrap">Saved</th>
            <th className="p-2 whitespace-nowrap">Notes</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id} className="border-b border-gray-200 dark:border-gray-700">
              <td className="p-2 whitespace-nowrap">{formatDate(run.started_at)}</td>
              <td className="p-2">{run.ig_username}</td>
              <td className="p-2">
                <StatusBadge value={run.status} />
              </td>
              <td className="p-2">{run.posts_fetched}</td>
              <td className="p-2">{run.posts_new}</td>
              <td className="p-2">{run.events_extracted}</td>
              <td className="p-2">{run.events_saved}</td>
              <td className="p-2 space-x-1">
                {run.pinned_post_warning && (
                  <span className="inline-flex items-center gap-1 text-xs text-amber-600">
                    <AlertTriangle className="h-3 w-3" /> pinned
                  </span>
                )}
                {run.error_message && (
                  <span className="text-xs text-red-500">{run.error_message}</span>
                )}
                {run.github_run_id && (
                  <a
                    href={`https://github.com/ericahan22/bug-free-octo-spork/actions/runs/${run.github_run_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-500 hover:underline"
                  >
                    GH#{run.github_run_id}
                  </a>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function GapsTable({ accounts }: { accounts: GapAccount[] }) {
  if (accounts.length === 0) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">No clubs found.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700 text-left text-gray-600 dark:text-gray-300">
            <th className="p-2 whitespace-nowrap">Club</th>
            <th className="p-2 whitespace-nowrap">IG Handle</th>
            <th className="p-2 whitespace-nowrap">Last Notification</th>
            <th className="p-2 whitespace-nowrap">Last Scrape</th>
            <th className="p-2 whitespace-nowrap">Last Event</th>
            <th className="p-2 whitespace-nowrap">Gap (days)</th>
            <th className="p-2 whitespace-nowrap">Status</th>
          </tr>
        </thead>
        <tbody>
          {accounts.map((account) => (
            <tr key={account.ig_handle} className="border-b border-gray-200 dark:border-gray-700">
              <td className="p-2">{account.club_name}</td>
              <td className="p-2 text-gray-500 dark:text-gray-400">@{account.ig_handle}</td>
              <td className="p-2 whitespace-nowrap">{formatDate(account.last_notification_at)}</td>
              <td className="p-2 whitespace-nowrap">
                {formatDate(account.last_scrape_at)}
                {account.last_scrape_status && (
                  <span className="ml-1 text-xs text-gray-400">({account.last_scrape_status})</span>
                )}
              </td>
              <td className="p-2 whitespace-nowrap">
                {account.last_event_at ? (
                  <span title={account.last_event_title || ""}>
                    {new Date(account.last_event_at).toLocaleDateString()}
                  </span>
                ) : (
                  "—"
                )}
              </td>
              <td className="p-2">{account.gap_days ?? "—"}</td>
              <td className="p-2">
                <StatusBadge value={account.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ScrapingDiagnosticsPage() {
  const navigate = useNavigate();
  const { logs, logsLoading, runs, runsLoading, gaps, gapsLoading } =
    useScrapingDiagnostics();

  const isLoading = logsLoading || runsLoading || gapsLoading;

  if (isLoading) {
    return <Loading message="Loading scraping diagnostics..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex flex-col gap-4 mb-8">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/admin")}
            className="flex items-center gap-2 w-fit"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Admin
          </Button>
          <h1 className="text-3xl font-bold">Scraping Diagnostics</h1>
        </div>

        {/* Summary */}
        {gaps && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold">{gaps.summary.total_clubs}</div>
              <div className="text-sm text-gray-500">Total Clubs</div>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-green-600">{gaps.summary.active_recently}</div>
              <div className="text-sm text-gray-500">Active (7d)</div>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-amber-600">{gaps.summary.stale}</div>
              <div className="text-sm text-gray-500">Stale</div>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-red-600">{gaps.summary.never_scraped}</div>
              <div className="text-sm text-gray-500">Never Scraped</div>
            </div>
          </div>
        )}

        {/* Notification Logs */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-2">
            Notification Logs
            {logs && logs.unresolved_count > 0 && (
              <span className="ml-2 text-sm text-red-500">
                ({logs.unresolved_count} unresolved)
              </span>
            )}
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <NotificationLogsTable logs={logs?.logs ?? []} />
          </div>
        </section>

        {/* Scrape Runs */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-2">
            Scrape Runs
            {runs && <span className="ml-2 text-sm text-gray-500">({runs.total} in last 7d)</span>}
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <ScrapeRunsTable runs={runs?.runs ?? []} />
          </div>
        </section>

        {/* Gaps */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-2">Stale Accounts</h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <GapsTable accounts={gaps?.accounts ?? []} />
          </div>
        </section>
      </div>
    </div>
  );
}
