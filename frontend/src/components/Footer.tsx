import React from "react";

function Footer() {
  return (
    <footer className="border-t border-gray-200/50 dark:border-gray-700/50 bg-white/60 dark:bg-gray-900/60 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-sm text-gray-600 dark:text-gray-400">
          <div className="space-y-1">
            <p>
              © {new Date().getFullYear()} Wat2Do in UWaterloo. All rights reserved.
            </p>
            <p>
              Feedback or issues? Email us at {" "}
              <a href="mailto:e22han@uwaterloo.ca" className="text-blue-500 hover:text-blue-600">
                e22han@uwaterloo.ca
              </a>{" "}
              and {" "}
              <a href="mailto:tqiu@uwaterloo.ca" className="text-blue-500 hover:text-blue-600">
                tqiu@uwaterloo.ca
              </a>
            </p>
          </div>

          <div className="flex items-center gap-4">
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


