import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import GitHubLink from "@/components/GitHubLink";
import { useTheme } from "@/hooks/useTheme";

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const isActive = (path: string) => {
    return (
      location.pathname === path ||
      (path === "/events" && location.pathname === "/")
    );
  };

  return (
    <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="text-base font-bold text-gray-900 dark:text-white">
              Wat2Do in UWaterloo
            </div>
            <div className="sm:ml-8 sm:flex sm:space-x-6">
              <Button
                onMouseDown={() => navigate("/events")}
                className={`text-sm font-medium ${
                  isActive("/events")
                    ? "text-gray-900 dark:text-white"
                    : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                Events
              </Button>
              <Button
                onMouseDown={() => navigate("/clubs")}
                className={`text-sm font-medium ${
                  isActive("/clubs")
                    ? "text-gray-900 dark:text-white"
                    : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                Clubs
              </Button>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <GitHubLink />
            <Button
              variant="ghost"
              size="sm"
              onMouseDown={toggleTheme}
              className="p-2"
            >
              {theme === "dark" ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default React.memo(Navbar);
