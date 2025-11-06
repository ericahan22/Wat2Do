import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { useAuth, useUser } from "@clerk/clerk-react";
import {
  ArrowLeft,
  Calendar,
  MapPin,
  DollarSign,
  Utensils,
  ExternalLink,
  Users,
  Save,
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Textarea } from "@/shared/components/ui/textarea";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { SEOHead } from "@/shared/components/SEOHead";
import { API_BASE_URL } from "@/shared/constants/api";
import { formatEventTimeRange, formatEventDate, formatRelativeEventDateWithTime } from "@/shared/lib/dateUtils";
import { getEventStatus, isEventNew } from "@/shared/lib/eventUtils";
import { Event } from "@/features/events/types/events";
import BadgeMask from "@/shared/components/ui/badge-mask";

const fetchEvent = async (eventId: string, token?: string | null): Promise<Event> => {
  const headers: HeadersInit = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const response = await fetch(`${API_BASE_URL}/events/${eventId}`, { headers });
  if (!response.ok) {
    throw new Error("Event not found");
  }
  return response.json();
};

const EventStatusBadge = ({ event }: { event: Event }) => {
  const status = getEventStatus(event);

  if (status === "live") {
    return (
      <BadgeMask variant="top-right">
        <Badge variant="live" className="font-extrabold">
          LIVE
        </Badge>
      </BadgeMask>
    );
  }

  if (status === "soon") {
    return (
      <BadgeMask variant="top-right">
        <Badge variant="soon" className="font-extrabold">
          Starting soon
        </Badge>
      </BadgeMask>
    );
  }

  return null;
};

const NewEventBadge = ({ event }: { event: Event }) => {
  if (!isEventNew(event)) return null;

  return (
    <BadgeMask variant="top-left">
      <Badge variant="new" className="font-extrabold">
        NEW
      </Badge>
    </BadgeMask>
  );
};

const OrganizationBadge = ({ event }: { event: Event }) => {
  if (!event.display_handle) return null;

  return (
    <BadgeMask variant="bottom-left">
      <Badge variant="outline" className="font-extrabold">
        {event.display_handle}
      </Badge>
    </BadgeMask>
  );
};

function EventDetailPage() {
  const { eventId } = useParams<{ eventId: string }>();
  const { user } = useUser();
  const isAdmin = user?.publicMetadata?.role === 'admin';
  const navigate = useNavigate();
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  
  const [editedData, setEditedData] = useState<any>(null);
  const [editError, setEditError] = useState<string | null>(null);

  const { data: event, isLoading, error } = useQuery({
    queryKey: ["event", eventId],
    queryFn: async () => {
        const token = await getToken();
      return fetchEvent(eventId!, token);
    },
    enabled: !!eventId,
  });

  // Initialize editedData when event loads for pending events or for admins
  useEffect(() => {
    if (event && !editedData) {
      const shouldEdit = (event.status === "PENDING" && (event as any).is_submitter) || isAdmin;
      if (shouldEdit) {
        const allowedFields = new Set(['title', 'dtstart', 'dtend', 'all_day', 'location', 'price', 'food', 'registration', 'description']);
        const filteredData: any = {};
        for (const field of Object.keys(event)) {
          if (allowedFields.has(field)) {
            filteredData[field] = event[field as keyof Event] ?? (field === 'all_day' || field === 'registration' ? false : field === 'price' ? null : "");
          }
        }
        setEditedData(filteredData);
      }
    }
  }, [event, editedData, isAdmin]);

  // Mutation for updating event
  const updateEventMutation = useMutation({
    mutationFn: async (eventData: any) => {
      const token = await getToken();
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      
      const response = await fetch(`${API_BASE_URL}/events/${eventId}/update/`, {
        method: "PUT",
        headers,
        body: JSON.stringify({ event_data: eventData }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to update event");
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["event", eventId] });
      setEditError(null);
    },
    onError: (error: Error) => {
      setEditError(error.message);
    },
  });

  const handleBack = () => {
    navigate(-1);
  };

  const handleExternalLink = () => {
    if (event?.source_url) {
      window.open(event.source_url, "_blank");
    }
  };

  const handleSaveEdit = () => {
    if (!editedData) {
      setEditError("No data to save");
      return;
    }
    updateEventMutation.mutate(editedData);
  };

  const handleFieldChange = (field: string, value: any) => {
    const updated = { ...editedData, [field]: value };
    setEditedData(updated);
    setEditError(null);
  };

  const canEditEvent = (event as any)?.is_submitter || isAdmin;
  const isPendingAndUnauthorized = event?.status === "PENDING" && !canEditEvent;

  // Show loading while either query is loading
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 dark:border-gray-100"></div>
          <span>Loading event...</span>
        </div>
      </div>
    );
  }

  // Show "Event Not Found" for actual errors, or if pending and unauthorized
  if (error || !event || isPendingAndUnauthorized) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Event Not Found
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          The event you're looking for doesn't exist or has been removed.
        </p>
        <Button onClick={handleBack} variant="outline">
          <ArrowLeft className="h-4 w-4" />
          Go Back
        </Button>
      </div>
    );
  }

  // Render edit mode for pending events when user has permission, OR for admins regardless of status
  if ((event.status === "PENDING" && canEditEvent) || isAdmin) {
    return (
      <div className="max-w-4xl mx-auto">
        <SEOHead
          title={`${event.title} - Edit Event`}
          description="Edit pending event details"
          url={`/event/${event.id}`}
        />

        {/* Back Button */}
        <div className="mb-6">
          <Button onMouseDown={handleBack} variant="ghost" className="p-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Events
          </Button>
        </div>

        {/* Original Screenshot (if available for submitter/admin) */}
        {(event as any)?.screenshot_url && (
          <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Original Screenshot</h2>
            <div className="relative w-full max-w-2xl mx-auto">
              <img
                src={(event as any).screenshot_url}
                alt="Original event screenshot"
                className="w-full h-auto rounded-lg shadow-lg"
              />
            </div>
          </div>
        )}

        {/* Edit Mode */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Edit Event Data</h2>
            <div className="flex gap-2">
              <Button
                onMouseDown={handleSaveEdit}
                disabled={updateEventMutation.isPending || !editedData}
                variant="default"
              >
                <Save className="h-4 w-4 mr-2" />
                {updateEventMutation.isPending ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
          
          {editError && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-300 text-sm">
              {editError}
            </div>
          )}
          
          {editedData && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 gap-4">
                {/* Title */}
                <div className="space-y-2">
                  <Label htmlFor="title" className="text-sm font-medium">
                    Title <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="title"
                    type="text"
                    value={editedData.title || ''}
                    onChange={(e) => handleFieldChange('title', e.target.value)}
                    placeholder="Event title"
                    disabled={updateEventMutation.isPending}
                    required
                  />
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description" className="text-sm font-medium">
                    Description
                  </Label>
          <Textarea
                    id="description"
                    value={editedData.description || ''}
                    onChange={(e) => handleFieldChange('description', e.target.value)}
                    placeholder="Event description"
                    disabled={updateEventMutation.isPending}
                    rows={4}
                  />
                </div>

                {/* Location */}
                <div className="space-y-2">
                  <Label htmlFor="location" className="text-sm font-medium">
                    Location <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="location"
                    type="text"
                    value={editedData.location || ''}
                    onChange={(e) => handleFieldChange('location', e.target.value)}
                    placeholder="Event location"
                    disabled={updateEventMutation.isPending}
                    required
                  />
                </div>

                {/* Date and Time */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="dtstart" className="text-sm font-medium">
                      Start Date & Time <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="dtstart"
                      type="text"
                      value={editedData.dtstart || ''}
                      onChange={(e) => handleFieldChange('dtstart', e.target.value)}
                      placeholder="2025-11-06 13:30:00-05"
                      disabled={updateEventMutation.isPending}
                      required
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Format: YYYY-MM-DD HH:MM:SS-TZ
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="dtend" className="text-sm font-medium">
                      End Date & Time
                    </Label>
                    <Input
                      id="dtend"
                      type="text"
                      value={editedData.dtend || ''}
                      onChange={(e) => handleFieldChange('dtend', e.target.value)}
                      placeholder="2025-11-06 15:30:00-05"
                      disabled={updateEventMutation.isPending}
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Leave empty if same as start time
                    </p>
                  </div>
                </div>

                {/* All Day Checkbox */}
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="all_day"
                    checked={editedData.all_day || false}
                    onCheckedChange={(checked) => handleFieldChange('all_day', checked === true)}
                    disabled={updateEventMutation.isPending}
                  />
                  <Label htmlFor="all_day" className="text-sm font-medium cursor-pointer">
                    All Day Event
                  </Label>
                </div>

                {/* Price */}
                <div className="space-y-2">
                  <Label htmlFor="price" className="text-sm font-medium">
                    Price
                  </Label>
                  <Input
                    id="price"
                    type="number"
                    step="0.01"
                    min="0"
                    value={editedData.price || ''}
                    onChange={(e) => handleFieldChange('price', e.target.value ? parseFloat(e.target.value) : null)}
                    placeholder="0.00"
                    disabled={updateEventMutation.isPending}
          />
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Leave empty for free events
                  </p>
                </div>

                {/* Food */}
                <div className="space-y-2">
                  <Label htmlFor="food" className="text-sm font-medium">
                    Food & Drinks
                  </Label>
                  <Input
                    id="food"
                    type="text"
                    value={editedData.food || ''}
                    onChange={(e) => handleFieldChange('food', e.target.value)}
                    placeholder="Free pizza and drinks"
                    disabled={updateEventMutation.isPending}
                  />
                </div>

                {/* Registration Checkbox */}
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="registration"
                    checked={editedData.registration || false}
                    onCheckedChange={(checked) => handleFieldChange('registration', checked === true)}
                    disabled={updateEventMutation.isPending}
                  />
                  <Label htmlFor="registration" className="text-sm font-medium cursor-pointer">
                    Registration Required
                  </Label>
                </div>
              </div>

              <p className="text-sm text-gray-500 dark:text-gray-400 pt-2">
                <span className="text-red-500">*</span> Required fields: <strong>title</strong>, <strong>dtstart</strong> (start date/time), and <strong>location</strong>.
                <br />
                <span className="text-xs mt-1 block text-gray-400 dark:text-gray-500">
                  Note: Timezone conversions, duration, coordinates, and other derived fields are computed automatically by the server.
                </span>
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Render normal event details for confirmed events
  return (
    <div className="max-w-4xl mx-auto">
      <SEOHead
        title={`${event.title} - Event Details`}
        description={
          event.description ||
          `Join us for ${event.title} on ${formatEventDate(event.dtstart || event.dtstart_utc, event.dtend || event.dtend_utc)}`
        }
        url={`/event/${event.id}`}
        keywords={[
          event.title,
          event.location || "",
          event.display_handle || "",
          "University of Waterloo",
          "event",
          "campus event",
        ].filter(Boolean)}
      />

      {/* Back Button */}
      <div className="mb-6">
        <Button onMouseDown={handleBack} variant="ghost" className="p-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Events
        </Button>
      </div>

      {/* Polaroid-style Event Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative max-w-lg mx-auto"
      >
        {/* Polaroid Frame */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-4 transform rotate-1 hover:rotate-0 transition-transform duration-300">
          {/* Image Section */}
          <div className="relative mb-4">
            {event.source_image_url ? (
              <div className="relative">
                <img
                  src={event.source_image_url}
                  alt={event.title}
                  className="w-full h-48 object-cover rounded-lg shadow-lg aspect-square"
                />
                <EventStatusBadge event={event} />
                <NewEventBadge event={event} />
                <OrganizationBadge event={event} />
              </div>
            ) : (
              <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-gray-700 dark:to-gray-600 rounded-lg shadow-lg flex items-center justify-center aspect-square">
                <div className="text-center">
                  <Calendar className="h-16 w-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400 text-lg">
                    No image available
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Event Details */}
          <div className="space-y-4">
            {/* Title */}
            <div>
              <h1 className="text-xl font-bold text-center text-gray-900 dark:text-white mb-2">
                {event.title}
              </h1>
              {event.description && (
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {event.description}
                </p>
              )}
            </div>

            {/* Event Info Grid */}
            <div className="grid gap-2">
              {/* Date & Time - Show all upcoming dates if available */}
              {event.upcoming_dates && event.upcoming_dates.length > 0 ? (
                <div className="p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3 mb-2">
                    <Calendar className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                    <p className="font-semibold text-gray-900 dark:text-white">
                      Upcoming Dates
                    </p>
                  </div>
                  <div className="ml-8 flex flex-wrap gap-2">
                    {event.upcoming_dates.map((date) => (
                      <Badge 
                        key={date.dtstart_utc}
                        variant="outline"
                        className="text-xs py-1 px-2 bg-white dark:bg-gray-800"
                      >
                        {formatRelativeEventDateWithTime(date.dtstart_utc, date.dtend_utc)}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <Calendar className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {formatEventDate(event.dtstart_utc)}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formatEventTimeRange(event.dtstart_utc, event.dtend_utc)}
                    </p>
                  </div>
                </div>
              )}

              {/* Location */}
              {event.location && (
                <div className="space-y-2">
                  <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <MapPin className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">
                        Location
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {event.location}
                      </p>
                    </div>
                  </div>
                  {/* Google Maps Embed - Only show for physical locations */}
                  {(() => {
                    const locationLower = event.location.toLowerCase();
                    const isVirtual = locationLower.includes("virtual") || 
                                     locationLower.includes("zoom") || 
                                     locationLower.includes("google meet");
                    return !isVirtual && (
                  <div className="w-full h-64 rounded-lg overflow-hidden">
                    <iframe
                      width="100%"
                      height="100%"
                      style={{ border: 0 }}
                      loading="lazy"
                      allowFullScreen
                      referrerPolicy="no-referrer-when-downgrade"
                      src={`https://www.google.com/maps/embed/v1/place?key=${
                        import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ""
                      }&q=${encodeURIComponent(`${event.location}, ${event.school || ""}`)}`}
                    ></iframe>
                  </div>
                    );
                  })()}
                </div>
              )}

              {/* Price */}
              <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <DollarSign className="h-5 w-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    Price
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {event.price === null || event.price === 0
                      ? "Free"
                      : `$${event.price}`}
                  </p>
                </div>
              </div>

              {/* Food */}
              {event.food && (
                <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <Utensils className="h-5 w-5 text-orange-600 dark:text-orange-400 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      Food
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {event.food}
                    </p>
                  </div>
                </div>
              )}

              {/* Registration */}
              {event.registration && (
                <div className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <Users className="h-5 w-5 text-purple-600 dark:text-purple-400 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      Registration
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Required
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Social Links */}
            {(event.ig_handle ||
              event.discord_handle ||
              event.x_handle ||
              event.tiktok_handle ||
              event.fb_handle) && (
              <div className="p-2 bg-gray-50 dark:bg-gray-700 rounded-lg flex flex-wrap gap-2">
                {event.ig_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-pink-50 dark:hover:bg-pink-900/20"
                  >
                    Instagram: {event.ig_handle}
                  </Badge>
                )}
                {event.discord_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-indigo-50 dark:hover:bg-indigo-900/20"
                  >
                    Discord: {event.discord_handle}
                  </Badge>
                )}
                {event.x_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20"
                  >
                    X: {event.x_handle}
                  </Badge>
                )}
                {event.tiktok_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900/20"
                  >
                    TikTok: {event.tiktok_handle}
                  </Badge>
                )}
                {event.fb_handle && (
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20"
                  >
                    Facebook: {event.fb_handle}
                  </Badge>
                )}
              </div>
            )}

            {/* Action Button */}
            {event.source_url && (
              <div className="text-center pt-2">
                <Button onClick={handleExternalLink}>
                  <ExternalLink className="h-4 w-4" />
                  View Event Source
                </Button>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Original Screenshot (if available for submitter/admin) */}
      {(event as any)?.screenshot_url && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-8 max-w-lg mx-auto"
        >
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 text-center">
              Original Screenshot
            </h3>
            <div className="relative w-full">
              <img
                src={(event as any).screenshot_url}
                alt="Original event screenshot"
                className="w-full h-auto rounded-lg shadow-lg"
              />
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default EventDetailPage;
