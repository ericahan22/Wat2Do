import { Moon, Sun, Menu, X, User, LogOut } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import GitHubLink from "./GitHubLink";
import { useNavbar } from "@/shared/hooks";
import { useAuth } from "@/shared/hooks/useAuth";
import { useNavigate } from "react-router-dom";

function Navbar() {
  const {
    isMobileMenuOpen,
    theme,
    isActive,
    toggleMobileMenu,
    toggleTheme,
  } = useNavbar();
  const navigate = useNavigate();

  const { isAuthenticated, user, logout, isLoggingOut } = useAuth();

  return (
    <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex gap-6 items-center">
            <img onMouseDown={() => navigate("/")} src="/wat2do-logo.svg" alt="Wat2Do" className="cursor-pointer h-14 w-14" />
            {/* Desktop Navigation */}
            <div className="hidden md:flex gap-2">
              <Button
                variant="link"
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
                variant="link"
                onMouseDown={() => navigate("/clubs")}
                className={`text-sm font-medium ${
                  isActive("/clubs")
                    ? "text-gray-900 dark:text-white"
                    : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                Clubs
              </Button>
              <Button
                variant="link"
                onMouseDown={() => navigate("/about")}
                className={`text-sm font-medium ${
                  isActive("/about")
                    ? "text-gray-900 dark:text-white"
                    : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                About
              </Button>
              <Button
                variant="link"
                onMouseDown={() => navigate("/contact")}
                className={`text-sm font-medium ${
                  isActive("/contact")
                    ? "text-gray-900 dark:text-white"
                    : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                Contact
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Desktop Right Side */}
            <div className="hidden md:flex items-center gap-2">
              <Button
                variant="link"
                asChild
                className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
              >
                <a
                  href="https://github.com/ericahan22/bug-free-octo-spork/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Feedback
                </a>
              </Button>
              <GitHubLink />

              {/* Auth Section */}
              {isAuthenticated ? (
                <div className="flex items-center gap-2">
                  <Button
                    variant="link"
                    className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={() => navigate("/dashboard")}
                  >
                    <User className="h-4 w-4" />
                    {user?.email}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onMouseDown={() => logout()}
                    disabled={isLoggingOut}
                    className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                  >
                    <LogOut className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <Button
                  variant="default"
                  className="text-sm font-medium"
                  onMouseDown={() => navigate("/auth")}
                >
                  <User className="h-4 w-4" />
                  Sign In
                </Button>
              )}
            </div>

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="sm"
              onMouseDown={toggleMobileMenu}
              className="md:hidden p-2"
            >
              {isMobileMenuOpen ? (
                <X className="h-4 w-4" />
              ) : (
                <Menu className="h-4 w-4" />
              )}
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onMouseDown={toggleTheme}
              className="p-2 h-9 w-9"
            >
              {theme === "dark" ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200/50 dark:border-gray-700/50 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md">
            <div className="px-4 py-2 space-y-1">
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => navigate("/events")}
              >
                Events
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => navigate("/clubs")}
              >
                Clubs
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => navigate("/about")}
              >
                About
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => navigate("/contact")}
              >
                Contact
              </Button>
              <div className="border-t border-gray-200/50 dark:border-gray-700/50 my-2"></div>

              {/* Mobile Auth Section */}
              {isAuthenticated ? (
                <div className="space-y-2">
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={() => {
                      navigate("/dashboard");
                    }}
                  >
                    <User className="h-4 w-4" />
                    {user?.email}
                  </Button>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={() => logout()}
                    disabled={isLoggingOut}
                  >
                    <LogOut className="h-4 w-4" />
                    Logout
                  </Button>
                </div>
              ) : (
                <Button
                  variant="default"
                  className="w-full justify-center text-sm font-medium"
                  onMouseDown={() => {
                    navigate("/auth");
                  }}
                >
                  <User className="h-4 w-4" />
                  Sign In
                </Button>
              )}

              <div className="border-t border-gray-200/50 dark:border-gray-700/50 my-2"></div>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  className="flex-1 justify-center text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                  asChild
                >
                  <a
                    href="https://github.com/ericahan22/bug-free-octo-spork/issues"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Feedback
                  </a>
                </Button>
                <div className="flex items-center">
                  <GitHubLink />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
