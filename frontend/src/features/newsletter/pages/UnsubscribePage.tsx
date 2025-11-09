import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import { Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { useUnsubscribe } from "@/features/newsletter/hooks/useUnsubscribe";
import UnsubscribeForm from "@/features/newsletter/components/UnsubscribeForm";

const UnsubscribePage: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();

  const {
    unsubscribeInfo,
    isLoading,
    isSubmitting,
    isSubmitSuccess,
    error,
    isError,
    email,
    isAlreadyUnsubscribed,
    isReady,
    unsubscribe,
  } = useUnsubscribe(token);

  const handleUnsubscribe = (reason: string, feedback?: string) => {
    unsubscribe(reason, feedback);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600" />
          <p className="">Loading...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (isError && !token) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 text-center flex flex-col gap-4">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
          <h1 className="text-xl font-bold ">
            Invalid Link
          </h1>
          <p className="">
            This unsubscribe link is invalid or has expired.
          </p>
          <Button onClick={() => navigate("/")} variant="outline">
            Goto events
          </Button>
        </Card>
      </div>
    );
  }

  if (isError && error) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 text-center flex flex-col gap-4">
          <h1 className="text-xl font-bold ">
            Error
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            An error occurred. Please try again later.
          </p>
          <Button onClick={() => navigate("/")} variant="outline">
            Goto events
          </Button>
        </Card>
      </div>
    );
  }

  // Success state
  if (isSubmitSuccess) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 text-center flex flex-col gap-4">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
          <h1 className="text-xl font-bold ">
            Successfully Unsubscribed
          </h1>
          <p className="">
            You have been successfully unsubscribed from the Wat2Do newsletter.
          </p>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
            <code className="text-sm text-blue-600 dark:text-blue-400">
              {email}
            </code>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Thank you for your feedback. We'll use it to improve our service.
          </p>
          <div className="flex flex-col gap-2">
            <Button
              variant="outline"
              onClick={() => navigate("/")}
              className="w-full"
            >
              Goto events
            </Button>
            <p className="text-xs text-gray-400">
              You can still discover events anytime at wat2do.ca
            </p>
          </div>
        </Card>
      </div>
    );
  }

  // Already unsubscribed state
  if (isAlreadyUnsubscribed) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 text-center flex flex-col gap-4">
          <CheckCircle className="h-12 w-12 text-gray-400 mx-auto" />
          <h1 className="text-xl font-bold ">
            Already Unsubscribed
          </h1>
          <p className="">
            You're already unsubscribed from our newsletter.
          </p>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
            <code className="text-sm text-blue-600 dark:text-blue-400">
              {email}
            </code>
          </div>
          {unsubscribeInfo?.unsubscribed_at && (
            <p className="text-xs text-gray-400">
              Unsubscribed on{" "}
              {new Date(unsubscribeInfo.unsubscribed_at).toLocaleDateString()}
            </p>
          )}
          <Button onClick={() => navigate("/")} variant="outline">
            Goto events
          </Button>
        </Card>
      </div>
    );
  }

  // Active unsubscribe form
  if (isReady && email) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 flex flex-col gap-6">
          <UnsubscribeForm
            email={email}
            onSubmit={handleUnsubscribe}
            isSubmitting={isSubmitting}
            error={error}
          />
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700 text-center">
            <p className="text-xs text-gray-400">
              Thanks for using Wat2Do - Your guide to UWaterloo events
            </p>
          </div>
        </Card>
      </div>
    );
  }

  // Fallback loading state
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
        <p className="">Loading...</p>
      </div>
    </div>
  );
};

export default UnsubscribePage;
