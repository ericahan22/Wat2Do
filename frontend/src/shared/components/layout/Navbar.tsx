import React from "react";
import { Link } from "react-router-dom";
import { Moon, Sun, Menu, X, Plus, User, LogOut } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import GitHubLink from "./GitHubLink";
import { useNavbar, useAuth } from "@/shared/hooks";

function Navbar() {
  const {
    isMobileMenuOpen,
    theme,
    isActive,
    toggleMobileMenu,
    closeMobileMenu,
    handleNavigation,
    toggleTheme,
  } = useNavbar();

  // Use the shared authentication hook
  const { isAuthenticated, isAdmin, email, logout } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.reload();
  };

  return (
    <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex gap-6 items-center">
            <div className="text-base font-bold">
              <Link to="/">
                <img
                  src="/wat2do-logo.svg"
                  alt="Wat2Do"
                  className="h-14 w-14"
                />
              </Link>
            </div>
            {/* Desktop Navigation */}
            <div className="hidden md:flex gap-2">
              <Button
                variant="link"
                onMouseDown={() => handleNavigation("/events")}
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
                onMouseDown={() => handleNavigation("/clubs")}
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
                onMouseDown={() => handleNavigation("/about")}
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
                onMouseDown={() => handleNavigation("/contact")}
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
              {isAuthenticated && (
                <>
                  <Button
                    variant="link"
                    onMouseDown={() => handleNavigation("/submit")}
                    className={`text-sm font-medium ${
                      isActive("/submit")
                        ? "text-gray-900 dark:text-white"
                        : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    }`}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Submit
                  </Button>
                  <Button
                    variant="link"
                    onMouseDown={() => handleNavigation("/my-submissions")}
                    className={`text-sm font-medium ${
                      isActive("/my-submissions")
                        ? "text-gray-900 dark:text-white"
                        : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    }`}
                  >
                    <User className="h-4 w-4 mr-1" />
                    My Submissions
                  </Button>
                  <Button
                    variant="link"
                    onMouseDown={() => handleNavigation("/promote-event")}
                    className={`text-sm font-medium ${
                      isActive("/promote-event")
                        ? "text-gray-900 dark:text-white"
                        : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    }`}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Promote Event
                  </Button>
                  {isAdmin && (
                    <Button
                      variant="link"
                      onMouseDown={() => handleNavigation("/admin/moderation")}
                      className={`text-sm font-medium ${
                        isActive("/admin/moderation")
                          ? "text-gray-900 dark:text-white"
                          : "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                      }`}
                    >
                      Admin
                    </Button>
                  )}
                </>
              )}
              {!isAuthenticated && (
                <Button
                  variant="link"
                  onMouseDown={() => handleNavigation("/login")}
                  className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                >
                  Login
                </Button>
              )}
              {isAuthenticated && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                            {email}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleLogout}
                    className="p-2"
                  >
                    <LogOut className="h-4 w-4" />
                  </Button>
                </div>
              )}
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
        
        {/* Mobile Dropdown Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200/50 dark:border-gray-700/50 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md">
            <div className="px-4 py-2 space-y-1">
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => handleNavigation("/events")}
              >
                Events
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => handleNavigation("/clubs")}
              >
                Clubs
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => handleNavigation("/about")}
              >
                About
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => handleNavigation("/contact")}
              >
                Contact
              </Button>
              {isAuthenticated && (
                <>
                  <div className="border-t border-gray-200/50 dark:border-gray-700/50 my-2"></div>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={() => handleNavigation("/submit")}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Submit
                  </Button>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={() => handleNavigation("/my-submissions")}
                  >
                    <User className="h-4 w-4 mr-2" />
                    My Submissions
                  </Button>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={() => handleNavigation("/promote-event")}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Promote Event
                  </Button>
                  {isAdmin && (
                    <Button
                      variant="ghost"
                      className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                      onMouseDown={() => handleNavigation("/admin/moderation")}
                    >
                      Admin
                    </Button>
                  )}
                </>
              )}
              {!isAuthenticated && (
                <>
                  <div className="border-t border-gray-200/50 dark:border-gray-700/50 my-2"></div>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={() => handleNavigation("/login")}
                  >
                    Login
                  </Button>
                </>
              )}
              {isAuthenticated && (
                <>
                  <div className="border-t border-gray-200/50 dark:border-gray-700/50 my-2"></div>
                  <div className="flex items-center justify-between px-2 py-1">
                    <span className="text-sm text-gray-600 dark:text-gray-300">
                            {email}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleLogout}
                      className="p-1"
                    >
                      <LogOut className="h-4 w-4" />
                    </Button>
                  </div>
                </>
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
                    onMouseDown={closeMobileMenu}
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

export default React.memo(Navbar);
