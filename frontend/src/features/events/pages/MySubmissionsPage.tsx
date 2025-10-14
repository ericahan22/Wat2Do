import { useState } from 'react';
import { Button } from '@/shared/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/components/ui/tabs';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { Plus, RefreshCw } from 'lucide-react';
import { useUserSubmissions } from '../hooks/useUserSubmissions';
import { useUserClubSubmissions } from '../../clubs/hooks/useUserClubSubmissions';
import { SubmissionStatusCard } from '../components/SubmissionStatusCard';
import { ClubSubmissionStatusCard } from '../../clubs/components/ClubSubmissionStatusCard';
import { EventSubmissionForm } from '../components/EventSubmissionForm';
import { ClubSubmissionForm } from '../../clubs/components/ClubSubmissionForm';

export function MySubmissionsPage() {
  const [showEventForm, setShowEventForm] = useState(false);
  const [showClubForm, setShowClubForm] = useState(false);
  
  const { 
    submissions: eventSubmissions, 
    isLoading: eventsLoading, 
    error: eventsError, 
    refetch: refetchEvents 
  } = useUserSubmissions();
  
  const { 
    submissions: clubSubmissions, 
    isLoading: clubsLoading, 
    error: clubsError, 
    refetch: refetchClubs 
  } = useUserClubSubmissions();

  const handleEventSubmitSuccess = () => {
    setShowEventForm(false);
    refetchEvents();
  };

  const handleClubSubmitSuccess = () => {
    setShowClubForm(false);
    refetchClubs();
  };

  const handleRefresh = () => {
    refetchEvents();
    refetchClubs();
  };

  if (showEventForm) {
    return (
      <div className="container mx-auto px-4 py-8">
        <EventSubmissionForm 
          onSuccess={handleEventSubmitSuccess}
          onCancel={() => setShowEventForm(false)}
        />
      </div>
    );
  }

  if (showClubForm) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ClubSubmissionForm 
          onSuccess={handleClubSubmitSuccess}
          onCancel={() => setShowClubForm(false)}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold">My Submissions</h1>
            <p className="text-gray-600 mt-2">
              Track the status of your submitted events and clubs
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={eventsLoading || clubsLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${(eventsLoading || clubsLoading) ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button onClick={() => setShowEventForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Submit Event
            </Button>
            <Button variant="outline" onClick={() => setShowClubForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Submit Club
            </Button>
          </div>
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
                <CardTitle>No Event Submissions</CardTitle>
                <CardDescription>
                  You haven't submitted any events yet. Click "Submit Event" to get started.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => setShowEventForm(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Submit Your First Event
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {eventSubmissions.map((submission) => (
                <SubmissionStatusCard 
                  key={submission.id} 
                  submission={submission} 
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
                <CardTitle>No Club Submissions</CardTitle>
                <CardDescription>
                  You haven't submitted any clubs yet. Click "Submit Club" to get started.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => setShowClubForm(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Submit Your First Club
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {clubSubmissions.map((submission) => (
                <ClubSubmissionStatusCard 
                  key={submission.id} 
                  submission={submission} 
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
