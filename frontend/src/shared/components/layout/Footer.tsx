import React, { useState } from "react";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Mail, Check, X, Rss } from "lucide-react";
import { useNewsletterSubscribe } from "@/features/newsletter/hooks/useNewsletterSubscribe";
import { useNavigate } from "react-router-dom";
import { getErrorMessage } from "@/shared/utils/errorUtils";

function Footer() {
  const [email, setEmail] = useState("");
  const navigate = useNavigate();
  const {
    subscribe,
    reset,
    isPending,
    isSuccess,
    isError,
    data,
    error,
  } = useNewsletterSubscribe();

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !email.includes("@")) {
      return;
    }

    subscribe({ email }, {
      onSuccess: () => {
        setEmail("");
        setTimeout(() => {
          reset();
        }, 5000);
      },
    });
  };

  return (
    <footer className="border-t border-gray-200/50 dark:border-gray-700/50 bg-white/60 dark:bg-gray-900/60 backdrop-blur-md mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Newsletter Section */}
        <div className="mb-8 pb-8 border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-md">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <Mail className="h-5 w-5" />
              Stay Updated
            </h3>
            <p className="text-sm mb-4">
              Get daily updates about upcoming events at UWaterloo delivered to
              your inbox.
            </p>

            <form
              onSubmit={handleSubscribe}
              className="flex flex-col sm:flex-row gap-2"
            >
              <Input
                type="email"
                placeholder="your.email@uwaterloo.ca"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isPending}
              />
              <Button
                variant="outline"
                type="submit"
                disabled={isPending}
                className="whitespace-nowrap h-9"
              >
                {isPending ? (
                  "Subscribing..."
                ) : isSuccess ? (
                  <>
                    <Check className="h-4 w-4 mr-1" />
                    Subscribed!
                  </>
                ) : (
                  "Subscribe"
                )}
              </Button>
            </form>

            {isSuccess && data && (
              <div className="mt-2 text-sm flex items-center gap-1 text-green-600 dark:text-green-400">
                <Check className="h-4 w-4" />
                {data.message}
              </div>
            )}

            {isError && !!error && (
              <div className="mt-2 text-sm flex items-center gap-1 text-red-600 dark:text-red-400">
                <X className="h-4 w-4" />
                {getErrorMessage(error)}
              </div>
            )}
          </div>
        </div>

        {/* Footer Links */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-sm">
          <div className="space-y-1">
            <p>
              © {new Date().getFullYear()} Wat2Do in UWaterloo. All rights
              reserved.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center">
            <a
              href="https://wat2do.instatus.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
            >
              <Button variant="ghost">
                <div className="relative">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <div className="absolute inset-0 w-2 h-2 bg-green-500 rounded-full animate-ping opacity-75"></div>
                </div>
                All systems operational
              </Button>
            </a>
            <Button
              variant="link"
              onMouseDown={() => navigate("/events")}
              className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              Events
            </Button>
            <Button
              variant="link"
              onMouseDown={() => navigate("/clubs")}
              className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              Clubs
            </Button>
            <Button
              variant="link"
              onMouseDown={() => navigate("/about")}
              className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              About
            </Button>
            <Button
              variant="link"
              onMouseDown={() => navigate("/contact")}
              className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              Contact
            </Button>
            <Button
              variant="link"
              onMouseDown={() => (window.location.href = "/rss.xml")}
              className="inline-flex items-center gap-0.5 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              <Rss className="h-4 w-4" />
              RSS
            </Button>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default React.memo(Footer);
