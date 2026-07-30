import React from "react";
import { Button } from "@/shared/components/ui/button";
import { Rss } from "lucide-react";
import { useNavigate } from "react-router-dom";

function Footer() {
  const navigate = useNavigate();

  return (
    <footer className="border-t border-gray-200/50 dark:border-gray-700/50 bg-white/60 dark:bg-gray-900/60 backdrop-blur-md mt-auto">
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row items-start justify-between gap-8 text-sm">
          <div className="space-y-1">
            <p className="h-9 flex items-center">
              © {new Date().getFullYear()} Wat2Do in UWaterloo. All rights
              reserved.
            </p>
            <p>
              Funded in part by the{" "}
              <span className="font-semibold">
                Student Life Endowment Fund (SLEF)
              </span>{" "}
              at the University of Waterloo.
            </p>
            <img
              src="/SLEF Logo_Color Logo Name.png"
              alt="SLEF Logo"
              width="120"
              className="h-auto"
            />
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center flex-wrap gap-2">
            <Button variant="ghost" asChild>
              <a
                href="https://wat2do.instatus.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
              >
                <div className="relative">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <div className="absolute inset-0 w-2 h-2 bg-green-500 rounded-full animate-ping opacity-75"></div>
                </div>
                All systems operational
              </a>
            </Button>
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
