import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { Loading } from "@/shared/components/ui/loading";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, AlertTriangle, Check, X } from "lucide-react";
import { useScrapingDiagnostics } from "@/features/admin/hooks/useScrapingDiagnostics";
import type { ScrapeRun, AutomateLog, GapAccount } from "@/features/admin/types/scraping";

const STATUS_LABELS: Record<string, string> = {
  success: "Success",
  error: "Error",
  running: "Running",
  no_posts: "No Events Saved",
  active: "Recent",
  stale: "Overdue",
  never_scraped: "Never Scraped",
};

function StatusBadge({ value }: { value: string }) {
  const variant =
    value === "success" || value === "active"
      ? "default"
      : value === "error"
        ? "destructive"
        : "secondary";
  return <Badge variant={variant}>{STATUS_LABELS[value] ?? value}</Badge>;
}

function BooleanIcon({ value }: { value: boolean }) {
  return value ? (
    <Check className="h-4 w-4 text-green-500" />
  ) : (
    <X className="h-4 w-4 text-red-500" />
  );
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
            <th className="p-2 whitespace-nowrap">Username Found</th>
            <th className="p-2 whitespace-nowrap">Scrape Triggered</th>
            <th className="p-2 whitespace-nowrap">Error</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id} className="border-b border-gray-200 dark:border-gray-700">
              <td className="p-2 whitespace-nowrap">{formatDate(log.created_at)}</td>
              <td className="p-2">{log.ig_username || log.ig_user_id || "—"}</td>
              <td className="p-2">
                <BooleanIcon value={log.username_resolved} />
              </td>
              <td className="p-2">
                <BooleanIcon value={log.dispatch_sent} />
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
            <th className="p-2 whitespace-nowrap">Posts Fetched</th>
            <th className="p-2 whitespace-nowrap">New Posts</th>
            <th className="p-2 whitespace-nowrap">Events Extracted</th>
            <th className="p-2 whitespace-nowrap">Events Saved</th>
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
            <th className="p-2 whitespace-nowrap">Last Event Added</th>
            <th className="p-2 whitespace-nowrap">Days Since Last Event</th>
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
        {gapsLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 animate-pulse">
                <div className="h-8 w-12 bg-gray-200 dark:bg-gray-700 rounded mb-1" />
                <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
              </div>
            ))}
          </div>
        ) : gaps && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold">{gaps.summary.total_clubs}</div>
              <div className="text-sm text-gray-500">Total Clubs</div>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-green-600">{gaps.summary.active_recently}</div>
              <div className="text-sm text-gray-500">Event Added in Last 7d</div>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-amber-600">{gaps.summary.stale}</div>
              <div className="text-sm text-gray-500">No Events in 7+ Days</div>
            </div>
            <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="text-2xl font-bold text-red-600">{gaps.summary.never_scraped}</div>
              <div className="text-sm text-gray-500">Never Scraped</div>
            </div>
          </div>
        )}

        {/* Notification Logs */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-1">
            IG Post Notifications
            {logs && logs.unresolved_count > 0 && (
              <span className="ml-2 text-sm text-red-500">
                ({logs.unresolved_count} unresolved)
              </span>
            )}
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
            Notifications caught by the Automate app when a club posts on Instagram.
          </p>
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            {logsLoading ? (
              <Loading message="Loading notifications..." />
            ) : (
              <NotificationLogsTable logs={logs?.logs ?? []} />
            )}
          </div>
        </section>

        {/* Scrape Runs */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-1">
            Scrape Runs
            {runs && <span className="ml-2 text-sm text-gray-500">({runs.total} in last 7d)</span>}
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
            Individual scraping jobs that fetch posts and extract events.
          </p>
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            {runsLoading ? (
              <Loading message="Loading scrape runs..." />
            ) : (
              <ScrapeRunsTable runs={runs?.runs ?? []} />
            )}
          </div>
        </section>

        {/* Club Scraping Health */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-1">Club Scraping Health</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
            How recently each club has had events added to the site.
          </p>
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            {gapsLoading ? (
              <Loading message="Loading club health..." />
            ) : (
              <GapsTable accounts={gaps?.accounts ?? []} />
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
