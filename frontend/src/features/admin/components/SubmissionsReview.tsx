import { useSubmissionsReview } from "@/features/admin/hooks/useSubmissionsReview";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Textarea } from "@/shared/components/ui/textarea";

const getStatusVariant = (status: string) => {
  if (status === "approved") return "success";
  if (status === "rejected") return "destructive";
  return "warning";
};

export function SubmissionsReview() {
  const {
    submissions,
    submissionsLoading,
    refetchSubmissions,
    processSubmission,
    handleReview,
    selectedSubmission,
    setSelectedSubmission,
    editedExtractedData,
    handleExtractedDataChange,
    parseError,
  } = useSubmissionsReview();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
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
            <p className="text-center py-8 text-gray-500">Loading submissions...</p>
          ) : submissions.length === 0 ? (
            <p className="text-center py-8 text-gray-500">No submissions found</p>
          ) : (
            <div className="space-y-3">
              {submissions.map((submission) => {
                const isSelected = selectedSubmission?.id === submission.id;
                return (
                  <Card
                    key={submission.id}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800"
                        : "hover:bg-gray-50 dark:hover:bg-gray-700"
                    }`}
                    onClick={() => setSelectedSubmission(submission)}
                  >
                    <CardContent className="pt-6">
                      <div className="flex justify-between items-start gap-4">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium mb-1">{submission.event_title}</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                            {submission.submitted_by_email && `By ${submission.submitted_by_email} • `}
                            {new Date(submission.submitted_at).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-gray-500 truncate">{submission.source_url}</p>
                        </div>
                        <Badge variant={getStatusVariant(submission.status)} className="shrink-0">
                          {submission.status}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Submission Details</CardTitle>
        </CardHeader>
        <CardContent>
          {selectedSubmission ? (
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">Screenshot</h3>
                <img
                  src={selectedSubmission.screenshot_url}
                  alt="Event screenshot"
                  className="w-full rounded border max-h-64 object-contain bg-gray-50 dark:bg-gray-900"
                />
              </div>

              <div>
                <h3 className="font-medium mb-2">Source URL</h3>
                <a
                  href={selectedSubmission.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 hover:underline text-sm break-all"
                >
                  {selectedSubmission.source_url}
                </a>
              </div>

              {selectedSubmission.extracted_data ? (
                <>
                  <div>
                    <h3 className="font-medium mb-2">Extracted Event Data</h3>
                    <Textarea
                      value={editedExtractedData}
                      onChange={(e) => handleExtractedDataChange(e.target.value)}
                      className={`min-h-32 font-mono text-sm ${parseError ? "border-red-500" : ""}`}
                    />
                    {parseError && (
                      <p className="text-sm text-red-500 mt-1">{parseError}</p>
                    )}
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button
                      onClick={() => handleReview("approve")}
                      variant="default"
                      className="flex-1"
                      disabled={!!parseError}
                    >
                      Approve
                    </Button>
                    <Button onClick={() => handleReview("reject")} variant="destructive" className="flex-1">
                      Reject
                    </Button>
                  </div>
                </>
              ) : (
                <Button onClick={() => processSubmission(selectedSubmission.id)} className="w-full">
                  Extract Event Data
                </Button>
              )}

              {selectedSubmission.admin_notes && (
                <div>
                  <h3 className="font-medium mb-2">Admin Notes</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                    {selectedSubmission.admin_notes}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-center text-gray-500 dark:text-gray-400 py-8">
              Select a submission to view details
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}



