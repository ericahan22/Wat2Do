import { Button } from "@/shared/components/ui/button";
import { useClerk } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useSubmissionsReview } from "@/features/admin/hooks/useSubmissionsReview";
import { Badge } from "@/shared/components/ui/badge";
import { Loading } from "@/shared/components/ui/loading";
import { getSubmissionStatusVariant } from "@/shared/lib/eventUtils";

export function SubmissionsReviewPage() {
  const { signOut } = useClerk();
  const navigate = useNavigate();
  const { submissions, submissionsLoading } = useSubmissionsReview();

  const handleLogout = () => {
    signOut();
  };

  if (submissionsLoading) {
    return <Loading message="Loading submissions..." />;
  }

  if (submissions.length === 0) {
    return <div>No submissions</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <div className="flex flex-col gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate("/admin")}
              className="flex items-center gap-2 w-fit"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Admin
            </Button>
            <h1 className="text-3xl font-bold">Event Submissions</h1>
          </div>
          <Button onClick={handleLogout} variant="destructive">
            Logout
          </Button>
        </div>

        <div className="space-y-2">
          {submissions.map((submission) => (
            <div
              key={submission.id}
              className="p-3 border rounded cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center gap-3"
              onClick={() =>
                submission.event_id &&
                navigate(`/events/${submission.event_id}`)
              }
            >
              <div className="flex-1">
                <div className="font-medium">
                  {submission.event_title || "Untitled"}
                </div>
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <span className="text-sm text-gray-500">
                    {new Date(submission.submitted_at).toLocaleDateString()}
                  </span>
                  {submission.submitted_by && (
                    <span className="text-sm text-gray-500">
                      • by {submission.submitted_by}
                    </span>
                  )}
                  <Badge variant={getSubmissionStatusVariant(submission.status)}>
                    {submission.status}
                  </Badge>
                </div>
              </div>
              {submission.source_image_url && (
                <img
                  src={submission.source_image_url}
                  alt="Event"
                  className="w-32 h-32 object-cover rounded"
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

