import React, { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Mail, Check, X } from "lucide-react";
import { useNewsletterSubscribe } from "@/hooks";

function Footer() {
  const [email, setEmail] = useState("");
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

    subscribe(email, {
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
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <Mail className="h-5 w-5" />
              Stay Updated
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
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
                disabled={isPending || isSuccess}
              />
              <Button
                variant="outline"
                type="submit"
                disabled={isPending || isSuccess}
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

            {isError && error && (
              <div className="mt-2 text-sm flex items-center gap-1 text-red-600 dark:text-red-400">
                <X className="h-4 w-4" />
                {error.message}
              </div>
            )}
          </div>
        </div>

        {/* Footer Links */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-sm text-gray-600 dark:text-gray-400">
          <div className="space-y-1">
            <p>
              © {new Date().getFullYear()} Wat2Do in UWaterloo. All rights
              reserved.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://wat2do.instatus.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
            >
              <Button>
                <div className="relative">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <div className="absolute inset-0 w-2 h-2 bg-green-500 rounded-full animate-ping opacity-75"></div>
                </div>
                <span>All systems operational</span>
              </Button>
            </a>
            <a
              href="/events"
              className="hover:text-gray-900 dark:hover:text-gray-200"
            >
              Events
            </a>
            <a
              href="/clubs"
              className="hover:text-gray-900 dark:hover:text-gray-200"
            >
              Clubs
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default React.memo(Footer);
