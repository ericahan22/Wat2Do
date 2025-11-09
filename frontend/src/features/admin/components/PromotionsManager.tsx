import { useEffect, useState, useCallback } from "react";
import { useEvents } from "@/features/events/hooks/useEvents";
import { useEventPromotion } from "@/features/admin/hooks/useEventPromotion";
import { useApi } from "@/shared/hooks/useApi";
import { handleError } from "@/shared/lib/errorHandler";
import type { EventPromotion, PromotedEvent } from "@/features/admin/types/promotion";
import { Event } from "@/features/events/types/events";
import { PromoteEventForm } from "@/features/admin/components/PromoteEventForm";
import { Button } from "@/shared/components/ui/button";
import { Label } from "@/shared/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";

export function PromotionsManager() {
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [selectedEventName, setSelectedEventName] = useState<string>("");
  const [isPromoted, setIsPromoted] = useState<boolean>(false);
  const [currentPromotion, setCurrentPromotion] = useState<EventPromotion | null>(null);

  const { adminAPIClient } = useApi();
  const { events, isLoading: eventsLoading } = useEvents();
  const { promotedEvents, promotedEventsLoading, refetchPromotedEvents } = useEventPromotion();

  const checkPromotionStatus = useCallback(async (eventId: string) => {
    try {
      const data = await adminAPIClient.getPromotionStatus(eventId);
      setIsPromoted(data.is_promoted);
      setCurrentPromotion(data.promotion);
    } catch (err) {
      // This is not a React Query function, so handle error directly
      handleError(err);
    }
  }, [adminAPIClient]);

  useEffect(() => {
    if (selectedEventId) {
      checkPromotionStatus(selectedEventId);
    }
  }, [selectedEventId, checkPromotionStatus]);

  const handleEventSelect = (eventId: string) => {
    const event = events.find((e: Event) => e.id.toString() === eventId);
    if (event) {
      setSelectedEventId(eventId);
      setSelectedEventName(event.title);
    }
  };

  const handleSuccess = () => {
    refetchPromotedEvents();
    if (selectedEventId) checkPromotionStatus(selectedEventId);
  };

  const handleCancel = () => {
    setSelectedEventId(null);
    setSelectedEventName("");
    setIsPromoted(false);
    setCurrentPromotion(null);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Select Event to Promote</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-6">
              <Label htmlFor="event-select" className="text-sm font-medium mb-2">
                Choose an Event
              </Label>
              <Select value={selectedEventId || ""} onValueChange={handleEventSelect} disabled={eventsLoading}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select an event..." />
                </SelectTrigger>
                <SelectContent>
                  {events.map((event: Event) => (
                    <SelectItem key={event.id} value={event.id.toString()}>
                      {event.title} (ID: {event.id})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {eventsLoading && <p className="text-sm text-gray-500 mt-1">Loading events...</p>}
            </div>

            {selectedEventId && (
              <Card className="mb-6 bg-gray-50 dark:bg-gray-700">
                <CardContent className="pt-6">
                  <h3 className="font-medium  mb-2">Current Status</h3>
                  <div className="text-sm  space-y-2">
                    <p>
                      <strong>Event:</strong> {selectedEventName}
                    </p>
                    <p>
                      <strong>ID:</strong> {selectedEventId}
                    </p>
                    <div className="flex items-center gap-2">
                      <strong>Promoted:</strong>
                      <Badge variant={isPromoted ? "default" : "secondary"}>{isPromoted ? "Yes" : "No"}</Badge>
                    </div>
                    {isPromoted && currentPromotion && (
                      <div className="mt-2 space-y-1">
                        <p>
                          <strong>Priority:</strong> {currentPromotion.priority}
                        </p>
                        <p>
                          <strong>Type:</strong> {currentPromotion.promotion_type}
                        </p>
                        <p>
                          <strong>Promoted At:</strong> {new Date(currentPromotion.promoted_at).toLocaleString()}
                        </p>
                        {currentPromotion.expires_at && (
                          <p>
                            <strong>Expires:</strong> {new Date(currentPromotion.expires_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {selectedEventId && (
              <PromoteEventForm
                eventId={selectedEventId}
                eventName={selectedEventName}
                isPromoted={isPromoted}
                currentPromotion={currentPromotion}
                onSuccess={handleSuccess}
                onCancel={handleCancel}
              />
            )}
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Currently Promoted Events</CardTitle>
              <Button onClick={() => refetchPromotedEvents()} size="sm" disabled={promotedEventsLoading}>
                {promotedEventsLoading ? "Loading..." : "Refresh"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {promotedEventsLoading ? (
              <p className=" text-center py-8">Loading promoted events...</p>
            ) : promotedEvents.length === 0 ? (
              <p className=" text-center py-8">No events are currently promoted</p>
            ) : (
              <div className="space-y-3">
                {promotedEvents.map((event: PromotedEvent) => (
                  <Card key={event.id} className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors" onClick={() => setSelectedEventId(event.id.toString())}>
                    <CardContent className="pt-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium ">{event.title}</h3>
                          <p className="text-sm ">{new Date(event.dtstart_utc).toLocaleDateString()} at {event.location}</p>
                        </div>
                        <div className="text-right space-y-2">
                          <Badge
                            variant={
                              event.promotion.promotion_type === "urgent"
                                ? "destructive"
                                : event.promotion.promotion_type === "featured"
                                ? "default"
                                : event.promotion.promotion_type === "sponsored"
                                ? "secondary"
                                : "outline"
                            }
                            className={
                              event.promotion.promotion_type === "sponsored"
                                ? "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
                                : ""
                            }
                          >
                            {event.promotion.promotion_type}
                          </Badge>
                          <p className="text-xs ">Priority: {event.promotion.priority}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Promotion Stats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{promotedEvents.length}</div>
                <div className="text-sm ">Total Promoted</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {promotedEvents.filter((e: PromotedEvent) => e.promotion.promotion_type === "featured").length}
                </div>
                <div className="text-sm ">Featured</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


