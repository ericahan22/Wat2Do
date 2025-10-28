import { useState } from "react";
import { useSubmissionsReview } from "@/features/admin/hooks/useSubmissionsReview";
import type { EventSubmission } from "@/features/events/types/submission";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";

export function SubmissionsReview() {
  const { submissions, submissionsLoading, refetchSubmissions, processSubmission, reviewSubmission } = useSubmissionsReview();
  const [selectedSubmission, setSelectedSubmission] = useState<EventSubmission | null>(null);

  const handleReviewed = () => setSelectedSubmission(null);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Event Submissions</CardTitle>
              <Button onClick={() => refetchSubmissions()} size="sm" disabled={submissionsLoading}>
                {submissionsLoading ? "Loading..." : "Refresh"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {submissionsLoading ? (
              <p className="text-center py-8">Loading submissions...</p>
            ) : submissions.length === 0 ? (
              <p className="text-center py-8">No pending submissions</p>
            ) : (
              <div className="space-y-3">
                {submissions.map((submission) => (
                  <Card
                    key={submission.id}
                    className={`cursor-pointer transition-colors ${
                      selectedSubmission?.id === submission.id
                        ? "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800"
                        : "hover:bg-gray-50 dark:hover:bg-gray-700"
                    }`}
                    onClick={() => setSelectedSubmission(submission)}
                  >
                    <CardContent className="pt-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium">Submission #{submission.id}</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {new Date(submission.submitted_at).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-500 truncate">{submission.source_url}</p>
                        </div>
                        <Badge
                          variant={
                            submission.status === "approved"
                              ? "default"
                              : submission.status === "rejected"
                              ? "destructive"
                              : "secondary"
                          }
                        >
                          {submission.status}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        {selectedSubmission ? (
          <Card>
            <CardHeader>
              <CardTitle>Submission Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">Screenshot</h3>
                <img src={selectedSubmission.screenshot_url} alt="Event screenshot" className="w-full rounded border max-h-64 object-contain" />
              </div>
              <div>
                <h3 className="font-medium mb-2">Source URL</h3>
                <a href={selectedSubmission.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline text-sm break-all">
                  {selectedSubmission.source_url}
                </a>
              </div>
              {selectedSubmission.extracted_data ? (
                <div>
                  <h3 className="font-medium mb-2">Extracted Event Data</h3>
                  <pre className="bg-gray-100 dark:bg-gray-800 p-3 rounded text-xs overflow-auto max-h-40">{JSON.stringify(selectedSubmission.extracted_data, null, 2)}</pre>
                </div>
              ) : (
                <div>
                  <Button onClick={() => processSubmission(selectedSubmission.id)} className="w-full">
                    Extract Event Data
                  </Button>
                </div>
              )}

              {selectedSubmission.extracted_data && (
                <div className="flex gap-2">
                  <Button
                    onClick={async () => {
                      await reviewSubmission({ submissionId: selectedSubmission.id, action: "approve" });
                      handleReviewed();
                    }}
                    variant="default"
                    className="flex-1"
                  >
                    Approve
                  </Button>
                  <Button
                    onClick={async () => {
                      await reviewSubmission({ submissionId: selectedSubmission.id, action: "reject" });
                      handleReviewed();
                    }}
                    variant="destructive"
                    className="flex-1"
                  >
                    Reject
                  </Button>
                </div>
              )}

              {selectedSubmission.admin_notes && (
                <div>
                  <h3 className="font-medium mb-2">Admin Notes</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{selectedSubmission.admin_notes}</p>
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-gray-500 dark:text-gray-400">Select a submission to view details</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}


