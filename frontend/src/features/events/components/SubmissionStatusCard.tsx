import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Badge } from '@/shared/components/ui/badge';
import { SubmittedEvent } from '../types/events';
import { format } from 'date-fns';
import { Calendar, MapPin, Clock, DollarSign, Users, ExternalLink } from 'lucide-react';

interface SubmissionStatusCardProps {
  submission: SubmittedEvent;
}

export function SubmissionStatusCard({ submission }: SubmissionStatusCardProps) {
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
            <CardTitle className="text-lg">{submission.name}</CardTitle>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="h-4 w-4" />
              {format(new Date(submission.date), 'MMM dd, yyyy')}
            </div>
          </div>
          <Badge className={getStatusColor(submission.status)}>
            {getStatusText(submission.status)}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Event Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-gray-500" />
            <span>
              {submission.start_time} - {submission.end_time || 'TBD'}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-gray-500" />
            <span>{submission.location}</span>
          </div>
          
          {submission.price && (
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-gray-500" />
              <span>${submission.price}</span>
            </div>
          )}
          
          {submission.registration && (
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-gray-500" />
              <span>Registration Required</span>
            </div>
          )}
        </div>

        {/* Club Information */}
        {submission.club_handle && (
          <div className="text-sm">
            <span className="font-medium">Club: </span>
            <span className="text-gray-600">@{submission.club_handle}</span>
          </div>
        )}

        {/* Description */}
        {submission.description && (
          <div className="text-sm">
            <span className="font-medium">Description: </span>
            <p className="text-gray-600 mt-1">{submission.description}</p>
          </div>
        )}

        {/* Event URL */}
        {submission.url && (
          <div className="flex items-center gap-2 text-sm">
            <ExternalLink className="h-4 w-4 text-gray-500" />
            <a 
              href={submission.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              View Event Details
            </a>
          </div>
        )}

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
