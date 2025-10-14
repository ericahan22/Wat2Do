import { Button } from '@/shared/components/ui/button';
import { Card, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/components/ui/tabs';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { RefreshCw } from 'lucide-react';
import { usePendingEventSubmissions, usePendingClubSubmissions } from '../hooks/usePendingSubmissions';
import { useEventModeration, useClubModeration } from '../hooks/useModeration';
import { ModerationCard } from '../components/ModerationCard';

export function ModerationPage() {
  const { 
    submissions: eventSubmissions, 
    isLoading: eventsLoading, 
    error: eventsError, 
    refetch: refetchEvents 
  } = usePendingEventSubmissions();
  
  const { 
    submissions: clubSubmissions, 
    isLoading: clubsLoading, 
    error: clubsError, 
    refetch: refetchClubs 
  } = usePendingClubSubmissions();

  const { moderateEvent, isLoading: eventModerating } = useEventModeration();
  const { moderateClub, isLoading: clubModerating } = useClubModeration();

  const handleEventModerate = async (id: number, status: 'approved' | 'rejected', rejectionReason?: string) => {
    await moderateEvent({ eventId: id, status, rejectionReason });
    refetchEvents();
  };

  const handleClubModerate = async (id: number, status: 'approved' | 'rejected', rejectionReason?: string) => {
    await moderateClub({ clubId: id, status, rejectionReason });
    refetchClubs();
  };

  const handleRefresh = () => {
    refetchEvents();
    refetchClubs();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold">Moderation Dashboard</h1>
            <p className="text-gray-600 mt-2">
              Review and approve pending event and club submissions
            </p>
          </div>
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={eventsLoading || clubsLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${(eventsLoading || clubsLoading) ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      <Tabs defaultValue="events" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="events">
            Events ({eventSubmissions.length})
          </TabsTrigger>
          <TabsTrigger value="clubs">
            Clubs ({clubSubmissions.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="events" className="mt-6">
          {eventsError && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{eventsError}</AlertDescription>
            </Alert>
          )}
          
          {eventsLoading ? (
            <div className="flex justify-center py-8">
              <RefreshCw className="h-8 w-8 animate-spin" />
            </div>
          ) : eventSubmissions.length === 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>No Pending Events</CardTitle>
                <CardDescription>
                  There are no pending event submissions to review.
                </CardDescription>
              </CardHeader>
            </Card>
          ) : (
            <div className="space-y-4">
              {eventSubmissions.map((submission) => (
                <ModerationCard 
                  key={submission.id} 
                  submission={submission}
                  type="event"
                  onModerate={handleEventModerate}
                  isModerating={eventModerating}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="clubs" className="mt-6">
          {clubsError && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{clubsError}</AlertDescription>
            </Alert>
          )}
          
          {clubsLoading ? (
            <div className="flex justify-center py-8">
              <RefreshCw className="h-8 w-8 animate-spin" />
            </div>
          ) : clubSubmissions.length === 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>No Pending Clubs</CardTitle>
                <CardDescription>
                  There are no pending club submissions to review.
                </CardDescription>
              </CardHeader>
            </Card>
          ) : (
            <div className="space-y-4">
              {clubSubmissions.map((submission) => (
                <ModerationCard 
                  key={submission.id} 
                  submission={submission}
                  type="club"
                  onModerate={handleClubModerate}
                  isModerating={clubModerating}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
