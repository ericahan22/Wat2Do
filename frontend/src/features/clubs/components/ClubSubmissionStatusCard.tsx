import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Badge } from '@/shared/components/ui/badge';
import { SubmittedClub } from '../types/clubs';
import { format } from 'date-fns';
import { ExternalLink, MessageSquare } from 'lucide-react';

interface ClubSubmissionStatusCardProps {
  submission: SubmittedClub;
}

export function ClubSubmissionStatusCard({ submission }: ClubSubmissionStatusCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'approved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pending Review';
      case 'approved':
        return 'Approved';
      case 'rejected':
        return 'Rejected';
      default:
        return status;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">{submission.club_name}</CardTitle>
            <div className="text-sm text-gray-600">
              {submission.categories}
            </div>
          </div>
          <Badge className={getStatusColor(submission.status)}>
            {getStatusText(submission.status)}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Club Type */}
        {submission.club_type && (
          <div className="text-sm">
            <span className="font-medium">Type: </span>
            <span className="text-gray-600">{submission.club_type}</span>
          </div>
        )}

        {/* Contact Information */}
        <div className="space-y-2">
          {submission.club_page && (
            <div className="flex items-center gap-2 text-sm">
              <ExternalLink className="h-4 w-4 text-gray-500" />
              <a 
                href={submission.club_page} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Website
              </a>
            </div>
          )}
          
          {submission.ig && (
            <div className="flex items-center gap-2 text-sm">
              <ExternalLink className="h-4 w-4 text-gray-500" />
              <a 
                href={submission.ig} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Instagram
              </a>
            </div>
          )}
          
          {submission.discord && (
            <div className="flex items-center gap-2 text-sm">
              <MessageSquare className="h-4 w-4 text-gray-500" />
              <a 
                href={submission.discord} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 underline"
              >
                Discord
              </a>
            </div>
          )}
        </div>

        {/* Rejection Reason */}
        {submission.status === 'rejected' && submission.rejection_reason && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <h4 className="font-medium text-red-800 mb-1">Rejection Reason:</h4>
            <p className="text-red-700 text-sm">{submission.rejection_reason}</p>
          </div>
        )}

        {/* Submission Info */}
        <div className="pt-3 border-t text-xs text-gray-500">
          <div>Submitted: {format(new Date(submission.submitted_at), 'MMM dd, yyyy HH:mm')}</div>
        </div>
      </CardContent>
    </Card>
  );
}
