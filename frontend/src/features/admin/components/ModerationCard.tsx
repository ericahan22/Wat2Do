import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Button } from '@/shared/components/ui/button';
import { Textarea } from '@/shared/components/ui/textarea';
import { Label } from '@/shared/components/ui/label';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { Badge } from '@/shared/components/ui/badge';
import { SubmittedEvent } from '../../events/types/events';
import { SubmittedClub } from '../../clubs/types/clubs';
import { format } from 'date-fns';
import { Calendar, MapPin, Clock, DollarSign, Users, ExternalLink, Check, X } from 'lucide-react';

interface ModerationCardProps {
  submission: SubmittedEvent | SubmittedClub;
  type: 'event' | 'club';
  onModerate: (id: number, status: 'approved' | 'rejected', rejectionReason?: string) => Promise<void>;
  isModerating: boolean;
}

export function ModerationCard({ submission, type, onModerate, isModerating }: ModerationCardProps) {
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleApprove = async () => {
    try {
      await onModerate(parseInt(submission.id), 'approved');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve submission');
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      setError('Rejection reason is required');
      return;
    }

    try {
      await onModerate(parseInt(submission.id), 'rejected', rejectionReason);
      setShowRejectForm(false);
      setRejectionReason('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reject submission');
    }
  };

  const isEvent = type === 'event';
  const eventSubmission = isEvent ? submission as SubmittedEvent : null;
  const clubSubmission = !isEvent ? submission as SubmittedClub : null;

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">
              {isEvent ? eventSubmission!.name : clubSubmission!.club_name}
            </CardTitle>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="h-4 w-4" />
              {format(new Date(submission.submitted_at), 'MMM dd, yyyy HH:mm')}
            </div>
          </div>
          <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">
            Pending Review
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Event-specific details */}
        {isEvent && eventSubmission && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span>
                  {eventSubmission.start_time} - {eventSubmission.end_time || 'TBD'}
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-gray-500" />
                <span>{eventSubmission.location}</span>
              </div>
              
              {eventSubmission.price && (
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-gray-500" />
                  <span>${eventSubmission.price}</span>
                </div>
              )}
              
              {eventSubmission.registration && (
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-gray-500" />
                  <span>Registration Required</span>
                </div>
              )}
            </div>

            {eventSubmission.club_handle && (
              <div className="text-sm">
                <span className="font-medium">Club: </span>
                <span className="text-gray-600">@{eventSubmission.club_handle}</span>
              </div>
            )}

            {eventSubmission.description && (
              <div className="text-sm">
                <span className="font-medium">Description: </span>
                <p className="text-gray-600 mt-1">{eventSubmission.description}</p>
              </div>
            )}

            {eventSubmission.url && (
              <div className="flex items-center gap-2 text-sm">
                <ExternalLink className="h-4 w-4 text-gray-500" />
                <a 
                  href={eventSubmission.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline"
                >
                  View Event Details
                </a>
              </div>
            )}

            {eventSubmission.image_url && (
              <div className="text-sm">
                <span className="font-medium">Image: </span>
                <a 
                  href={eventSubmission.image_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline ml-2"
                >
                  View Image
                </a>
              </div>
            )}
          </>
        )}

        {/* Club-specific details */}
        {!isEvent && clubSubmission && (
          <>
            <div className="text-sm">
              <span className="font-medium">Categories: </span>
              <span className="text-gray-600">{clubSubmission.categories}</span>
            </div>

            {clubSubmission.club_type && (
              <div className="text-sm">
                <span className="font-medium">Type: </span>
                <span className="text-gray-600">{clubSubmission.club_type}</span>
              </div>
            )}

            <div className="space-y-2">
              {clubSubmission.club_page && (
                <div className="flex items-center gap-2 text-sm">
                  <ExternalLink className="h-4 w-4 text-gray-500" />
                  <a 
                    href={clubSubmission.club_page} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline"
                  >
                    Website
                  </a>
                </div>
              )}
              
              {clubSubmission.ig && (
                <div className="flex items-center gap-2 text-sm">
                  <ExternalLink className="h-4 w-4 text-gray-500" />
                  <a 
                    href={clubSubmission.ig} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline"
                  >
                    Instagram
                  </a>
                </div>
              )}
              
              {clubSubmission.discord && (
                <div className="flex items-center gap-2 text-sm">
                  <ExternalLink className="h-4 w-4 text-gray-500" />
                  <a 
                    href={clubSubmission.discord} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline"
                  >
                    Discord
                  </a>
                </div>
              )}
            </div>
          </>
        )}

        {/* Rejection form */}
        {showRejectForm && (
          <div className="space-y-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <Label htmlFor="rejectionReason">Rejection Reason *</Label>
            <Textarea
              id="rejectionReason"
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Please provide a reason for rejection..."
              rows={3}
            />
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="destructive"
                onClick={handleReject}
                disabled={isModerating}
              >
                <X className="h-4 w-4 mr-2" />
                {isModerating ? 'Rejecting...' : 'Reject'}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setShowRejectForm(false);
                  setRejectionReason('');
                  setError(null);
                }}
              >
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Action buttons */}
        {!showRejectForm && (
          <div className="flex gap-2 pt-4 border-t">
            <Button
              onClick={handleApprove}
              disabled={isModerating}
              className="bg-green-600 hover:bg-green-700"
            >
              <Check className="h-4 w-4 mr-2" />
              {isModerating ? 'Approving...' : 'Approve'}
            </Button>
            <Button
              variant="destructive"
              onClick={() => setShowRejectForm(true)}
              disabled={isModerating}
            >
              <X className="h-4 w-4 mr-2" />
              Reject
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
