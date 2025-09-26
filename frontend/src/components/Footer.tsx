import React from "react";
import { Button } from "./ui/button";

function Footer() {
  return (
    <footer className="border-t border-gray-200/50 dark:border-gray-700/50 bg-white/60 dark:bg-gray-900/60 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
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
