import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import { Loader2, CheckCircle, AlertCircle, Mail } from "lucide-react";
import { useWaitlist } from "@/features/waitlist/hooks/useWaitlist";

const WaitlistPage: React.FC = () => {
  const { schoolSlug } = useParams<{ schoolSlug: string }>();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");

  const {
    schoolInfo,
    isLoading,
    isSubmitting,
    isSubmitSuccess,
    submitData,
    isFetchError,
    isReady,
    joinWaitlist,
    errorMessage,
    resetSubmit,
  } = useWaitlist(schoolSlug);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim()) {
      joinWaitlist(email.trim());
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600" />
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // School not found
  if (isFetchError || !schoolSlug) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 text-center flex flex-col gap-4">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
          <h1 className="text-xl font-bold">School Not Found</h1>
          <p className="text-gray-600 dark:text-gray-400">
            This school is not currently on our waitlist.
          </p>
          <Button onClick={() => navigate("/")} variant="outline">
            Go to events
          </Button>
        </Card>
      </div>
    );
  }

  // Success state
  if (isSubmitSuccess && submitData) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 text-center flex flex-col gap-4">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
          <h1 className="text-xl font-bold">You're on the waitlist!</h1>
          <p className="text-gray-600 dark:text-gray-400">
            We'll notify you when {submitData.school} launches on Wat2Do.
          </p>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
            <code className="text-sm text-blue-600 dark:text-blue-400">
              {submitData.email}
            </code>
          </div>
          <Button onClick={() => navigate("/")} variant="outline">
            Explore Waterloo events
          </Button>
        </Card>
      </div>
    );
  }

  // Waitlist form
  if (isReady && schoolInfo) {
    const isAlreadyOnList = submitData?.message?.includes("already");

    const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setEmail(e.target.value);
      // Clear error when user starts typing again
      if (errorMessage) {
        resetSubmit();
      }
    };

    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 flex flex-col gap-6">
          <div className="text-center">
            <Mail className="h-12 w-12 text-blue-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold mb-2">Join the Waitlist</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Be the first to know when {schoolInfo.name} events launch on Wat2Do.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                University Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder={`your.name@${schoolInfo.domains[0]}`}
                value={email}
                onChange={handleEmailChange}
                disabled={isSubmitting}
                className={errorMessage ? "border-red-500 focus:border-red-500 focus:ring-red-500" : ""}
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Accepted domains: {schoolInfo.domains.join(", ")}
              </p>
              {errorMessage && (
                <div className="flex items-center gap-2 mt-2">
                  <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                  <p className="text-sm text-red-500">{errorMessage}</p>
                </div>
              )}
              {isAlreadyOnList && (
                <div className="flex items-center gap-2 mt-2">
                  <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                  <p className="text-sm text-green-600">
                    You're already on the waitlist!
                  </p>
                </div>
              )}
            </div>

            <Button type="submit" disabled={isSubmitting || !email.trim()}>
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Joining...
                </>
              ) : (
                "Join Waitlist"
              )}
            </Button>
          </form>

          <div className="pt-4 border-t border-gray-200 dark:border-gray-700 text-center">
            <p className="text-xs text-gray-400">
              We'll only use your email to notify you when {schoolInfo.name} launches.
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
        <p>Loading...</p>
      </div>
    </div>
  );
};

export default WaitlistPage;
