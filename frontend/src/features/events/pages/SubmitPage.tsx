import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Button } from '@/shared/components/ui/button';
import { EventSubmissionForm } from '../components/EventSubmissionForm';
import { ClubSubmissionForm } from '../../clubs/components/ClubSubmissionForm';
import { Plus, Users } from 'lucide-react';

export function SubmitPage() {
  const [selectedType, setSelectedType] = useState<'event' | 'club' | null>(null);

  if (selectedType === 'event') {
    return (
      <div className="container mx-auto px-4 py-8">
        <EventSubmissionForm 
          onSuccess={() => setSelectedType(null)}
          onCancel={() => setSelectedType(null)}
        />
      </div>
    );
  }

  if (selectedType === 'club') {
    return (
      <div className="container mx-auto px-4 py-8">
        <ClubSubmissionForm 
          onSuccess={() => setSelectedType(null)}
          onCancel={() => setSelectedType(null)}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-4">Submit Content</h1>
          <p className="text-gray-600 text-lg">
            Share events and clubs with the Waterloo community. All submissions are reviewed before being published.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => setSelectedType('event')}>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Plus className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <CardTitle>Submit Event</CardTitle>
                  <CardDescription>
                    Share an upcoming event with the community
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Submit events like workshops, social gatherings, competitions, and more. 
                Include details like date, time, location, and description.
              </p>
              <Button className="w-full">
                Submit Event
              </Button>
            </CardContent>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => setSelectedType('club')}>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-green-100 rounded-lg">
                  <Users className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <CardTitle>Submit Club</CardTitle>
                  <CardDescription>
                    Add a new club to the directory
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Submit new clubs, societies, or organizations. 
                Include contact information and social media links.
              </p>
              <Button className="w-full">
                Submit Club
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8 p-6 bg-gray-50 rounded-lg">
          <h3 className="font-semibold mb-2">Submission Guidelines</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• All submissions are reviewed by moderators before being published</li>
            <li>• Events must be in the future and open to Waterloo students</li>
            <li>• Clubs must be legitimate student organizations</li>
            <li>• Provide accurate and complete information</li>
            <li>• Include high-quality images for events</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
