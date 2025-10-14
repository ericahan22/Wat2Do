import { useState, useEffect, memo } from "react";
import { PromoteEventForm } from "@/features/admin/components/PromoteEventForm";
import { AdminLogin } from "@/features/admin/components/AdminLogin";
import { useEvents } from "@/features/events/hooks/useEvents";
import { useEventPromotion } from "@/features/admin/hooks/useEventPromotion";
import { API_BASE_URL } from "@/shared/constants/api";
import type { EventPromotion, PromotedEvent } from "@/features/admin/types/promotion";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/components/ui/select";
import { Event } from "@/features/events/types/events";

/**
 * Admin page for managing event promotions
 * Requires admin authentication
 */
function AdminPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [selectedEventName, setSelectedEventName] = useState<string>("");
  const [isPromoted, setIsPromoted] = useState<boolean>(false);
  const [currentPromotion, setCurrentPromotion] = useState<EventPromotion | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Use the existing events hook
  const {
    data: events,
    isLoading: eventsLoading,
    error: eventsError,
  } = useEvents();

  // Check authentication on component mount
  useEffect(() => {
    const token = localStorage.getItem("admin_token");
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  // Load events when selected event changes
  useEffect(() => {
    if (selectedEventId) {
      checkPromotionStatus(selectedEventId);
    }
  }, [selectedEventId]);

  const {
    promotedEvents,
    promotedEventsLoading,
    promotedEventsError,
    refetchPromotedEvents,
  } = useEventPromotion();

  const checkPromotionStatus = async (eventId: string) => {
    try {
      const token = localStorage.getItem("admin_token");
      if (!token) return;

      const response = await fetch(
        `${API_BASE_URL}/promotions/events/${eventId}/promotion-status/`,
        {
          headers: {
            Authorization: `Token ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setIsPromoted(data.is_promoted);
        setCurrentPromotion(data.promotion);
      }
    } catch (err) {
      console.error("Error checking promotion status:", err);
    }
  };

  const handleEventSelect = (eventId: string) => {
    const event = events.find((e: Event) => e.id === eventId);
    if (event) {
      setSelectedEventId(eventId);
      setSelectedEventName(event.name);
    }
  };

  const handleSuccess = () => {
    // Refresh promoted events list
    refetchPromotedEvents();
    // Refresh promotion status for selected event
    if (selectedEventId) {
      checkPromotionStatus(selectedEventId);
    }
  };

  const handleCancel = () => {
    setSelectedEventId(null);
    setSelectedEventName("");
    setIsPromoted(false);
    setCurrentPromotion(null);
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
    refetchPromotedEvents();
  };

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    setIsAuthenticated(false);
    setSelectedEventId(null);
    setSelectedEventName("");
    setIsPromoted(false);
    setCurrentPromotion(null);
  };

  // Show login form if not authenticated
  if (!isAuthenticated) {
    return <AdminLogin onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold ">
            Event Promotion Admin
          </h1>
          <Button onClick={handleLogout} variant="destructive">
            Logout
          </Button>
        </div>

        {error && (
          <Card className="mb-6 border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-red-400"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                      Error
                    </h3>
                    <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                      {error}
                    </div>
                  </div>
                </div>
                <Button
                  onClick={() => setError(null)}
                  variant="ghost"
                  size="sm"
                  className="text-red-500 hover:text-red-700 hover:bg-red-100 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-800/20"
                >
                  ×
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Event Selection & Form */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Select Event to Promote</CardTitle>
              </CardHeader>
              <CardContent>
                {/* Event Selection */}
                <div className="mb-6">
                  <label
                    htmlFor="event-select"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                  >
                    Choose an Event
                  </label>
                  <Select
                    value={selectedEventId || ""}
                    onValueChange={handleEventSelect}
                    disabled={eventsLoading}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select an event..." />
                    </SelectTrigger>
                    <SelectContent>
                      {events.map((event: Event) => (
                        <SelectItem key={event.id} value={event.id}>
                          {event.name} (ID: {event.id})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {eventsLoading && (
                    <p className="text-sm text-gray-500 mt-1">
                      Loading events...
                    </p>
                  )}
                  {eventsError && (
                    <p className="text-sm text-red-500 mt-1">
                      Error loading events: {eventsError.message}
                    </p>
                  )}
                </div>

                {/* Current Status */}
                {selectedEventId && (
                  <Card className="mb-6 bg-gray-50 dark:bg-gray-700">
                    <CardContent className="pt-6">
                      <h3 className="font-medium  mb-2">
                        Current Status
                      </h3>
                      <div className="text-sm  space-y-2">
                        <p>
                          <strong>Event:</strong> {selectedEventName}
                        </p>
                        <p>
                          <strong>ID:</strong> {selectedEventId}
                        </p>
                        <div className="flex items-center gap-2">
                          <strong>Promoted:</strong>
                          <Badge variant={isPromoted ? "default" : "secondary"}>
                            {isPromoted ? "Yes" : "No"}
                          </Badge>
                        </div>
                        {isPromoted && currentPromotion && (
                          <div className="mt-2 space-y-1">
                            <p>
                              <strong>Priority:</strong>{" "}
                              {currentPromotion.priority}
                            </p>
                            <p>
                              <strong>Type:</strong>{" "}
                              {currentPromotion.promotion_type}
                            </p>
                            <p>
                              <strong>Promoted At:</strong>{" "}
                              {new Date(
                                currentPromotion.promoted_at
                              ).toLocaleString()}
                            </p>
                            {currentPromotion.expires_at && (
                              <p>
                                <strong>Expires:</strong>{" "}
                                {new Date(
                                  currentPromotion.expires_at
                                ).toLocaleString()}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Promotion Form */}
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

          {/* Right Column: Promoted Events List */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Currently Promoted Events</CardTitle>
                  <Button
                    onClick={() => refetchPromotedEvents()}
                    size="sm"
                    disabled={promotedEventsLoading}
                  >
                    {promotedEventsLoading ? "Loading..." : "Refresh"}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {promotedEventsLoading ? (
                  <p className=" text-center py-8">
                    Loading promoted events...
                  </p>
                ) : promotedEventsError ? (
                  <p className="text-red-500 text-center py-8">
                    Error loading promoted events: {promotedEventsError.message}
                  </p>
                ) : promotedEvents.length === 0 ? (
                  <p className=" text-center py-8">
                    No events are currently promoted
                  </p>
                ) : (
                  <div className="space-y-3">
                    {promotedEvents.map((event: PromotedEvent) => (
                      <Card
                        key={event.id}
                        className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        onClick={() => handleEventSelect(event.id)}
                      >
                        <CardContent className="pt-6">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h3 className="font-medium ">
                                {event.name}
                              </h3>
                              <p className="text-sm ">
                                {new Date(event.date).toLocaleDateString()} at{" "}
                                {event.location}
                              </p>
                            </div>
                            <div className="text-right space-y-2">
                              <Badge
                                variant={
                                  event.promotion.promotion_type === "urgent"
                                    ? "destructive"
                                    : event.promotion.promotion_type ===
                                      "featured"
                                    ? "default"
                                    : event.promotion.promotion_type ===
                                      "sponsored"
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
                              <p className="text-xs ">
                                Priority: {event.promotion.priority}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Promotion Stats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {promotedEvents.length}
                    </div>
                    <div className="text-sm ">
                      Total Promoted
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                      {
                        promotedEvents.filter(
                          (e) => e.promotion.promotion_type === "featured"
                        ).length
                      }
                    </div>
                    <div className="text-sm ">
                      Featured
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

export default memo(AdminPage);
