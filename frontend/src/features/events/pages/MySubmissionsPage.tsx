import { useUserSubmissions } from "@/features/events/hooks/useUserSubmissions";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  Calendar,
  ExternalLink,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Trash2,
} from "lucide-react";
import { formatPrettyDate } from "@/shared/lib/dateUtils";
import type { EventSubmission } from "@/features/events/types/submission";
import { useNavigate } from "react-router-dom";
import { useClerk } from "@clerk/clerk-react";

export function MySubmissionsPage() {
  const {
    data: submissions = [],
    isLoading,
    removeSubmission,
    isDeleting,
  } = useUserSubmissions();
  const navigate = useNavigate();
  const { signOut } = useClerk();
  // Type assertion to fix TypeScript issues
  const submissionsArray = submissions as EventSubmission[];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "rejected":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "pending":
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "approved":
        return "default" as const;
      case "rejected":
        return "destructive" as const;
      case "pending":
        return "secondary" as const;
      default:
        return "outline" as const;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">
              Loading your submissions...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              My Event Submissions
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Track the status of your submitted events
            </p>
          </div>
          <Button variant="outline" onMouseDown={() => signOut()}>Logout</Button>
        </div>

        {/* Submissions Grid */}
        {submissionsArray.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                  No submissions yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Submit your first event to get started!
                </p>
                <Button onClick={() => navigate("/submit")}>
                  Submit Event
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {submissionsArray.map((submission) => (
              <Card
                key={submission.id}
                className="hover:shadow-lg transition-shadow"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(submission.status)}
                      <CardTitle className="text-lg">
                        Submission #{submission.id}
                      </CardTitle>
                    </div>
                    <Badge variant={getStatusBadgeVariant(submission.status)}>
                      {submission.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Screenshot */}
                  <div>
                    <img
                      src={submission.screenshot_url}
                      alt="Event screenshot"
                      className="w-full h-32 object-cover rounded border"
                    />
                  </div>

                  {/* Source URL */}
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <ExternalLink className="h-4 w-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Source
                      </span>
                    </div>
                    <a
                      href={submission.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 dark:text-blue-400 hover:underline break-all"
                    >
                      {submission.source_url}
                    </a>
                  </div>

                  {/* Timestamps */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-gray-500" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Submitted: {formatPrettyDate(submission.submitted_at)}
                      </span>
                    </div>
                    {submission.reviewed_at && (
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-gray-500" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Reviewed: {formatPrettyDate(submission.reviewed_at)}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Admin Notes */}
                  {submission.admin_notes && (
                    <div>
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Admin Notes:
                      </span>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {submission.admin_notes}
                      </p>
                    </div>
                  )}

                  {/* Created Event Link */}
                  {submission.created_event_id && (
                    <div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          navigate(`/events/${submission.created_event_id}`)
                        }
                        className="w-full"
                      >
                        View Created Event
                      </Button>
                    </div>
                  )}

                  {/* Remove Button (only if not approved) */}
                  {submission.status !== "approved" && (
                    <Button
                      variant="destructive"
                      size="sm"
                      className="w-full"
                      disabled={isDeleting}
                      onClick={() => {
                        const confirmed = window.confirm(
                          "Remove this submission? If it created an event, that event will also be removed. This cannot be undone."
                        );
                        if (confirmed) {
                          removeSubmission(submission.id);
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Remove Submission
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
