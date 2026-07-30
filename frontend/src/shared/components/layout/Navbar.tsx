import { Moon, Sun, Menu, X, User, LogOut } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { useNavbar } from "@/shared/hooks";
import { useNavigate } from "react-router-dom";
import { logout, useAuthState } from "@/features/auth/hooks/useAuthState";

function Navbar() {
  const {
    isMobileMenuOpen,
    theme,
    isActive,
    toggleMobileMenu,
    toggleTheme,
  } = useNavbar();
  const navigate = useNavigate();
  const { isSignedIn, user } = useAuthState();

  const handleLogout = async () => {
    await logout();
    navigate("/events");
  };

  return (
    <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex gap-6 items-center">
            <img
              onMouseDown={() => navigate("/")}
              src="/wat2do-logo.svg"
              alt="Wat2Do"
              className="cursor-pointer h-14 w-14"
            />
            <div className="hidden md:flex gap-1">
              <Button
                variant="ghost"
                onMouseDown={() => navigate("/events")}
                className={`text-sm font-medium transition-colors hover:underline ${isActive("/events") || isActive("/")
                  ? "bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300"
                  : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white"
                  }`}
              >
                Events
              </Button>

              <Button
                variant="ghost"
                onMouseDown={() => navigate("/clubs")}
                className={`text-sm font-medium transition-colors hover:underline ${isActive("/clubs")
                  ? "bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300"
                  : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white"
                  }`}
              >
                Clubs
              </Button>

              <Button
                variant="ghost"
                onMouseDown={() => navigate("/about")}
                className={`text-sm font-medium transition-colors hover:underline ${isActive("/about")
                  ? "bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300"
                  : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white"
                  }`}
              >
                About
              </Button>

              <Button
                variant="ghost"
                onMouseDown={() => navigate("/contact")}
                className={`text-sm font-medium transition-colors hover:underline ${isActive("/contact")
                  ? "bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300"
                  : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white"
                  }`}
              >
                Contact
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="hidden md:flex items-center gap-2">
              {isSignedIn ? (
                <>
                  <span className="max-w-48 truncate text-sm text-gray-600 dark:text-gray-300">
                    {user?.email}
                  </span>
                  <Button
                    variant="ghost"
                    className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={handleLogout}
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </Button>
                </>
              ) : (
                <Button
                  variant="default"
                  className="text-sm font-medium"
                  onMouseDown={() => navigate("/login")}
                >
                  <User className="h-4 w-4" />
                  Sign in
                </Button>
              )}
            </div>

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

        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200/50 dark:border-gray-700/50 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md">
            <div className="px-4 py-2 space-y-1">
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => {
                  navigate("/events");
                  toggleMobileMenu();
                }}
              >
                Events
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => {
                  navigate("/clubs");
                  toggleMobileMenu();
                }}
              >
                Clubs
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => {
                  navigate("/about");
                  toggleMobileMenu();
                }}
              >
                About
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                onMouseDown={() => {
                  navigate("/contact");
                  toggleMobileMenu();
                }}
              >
                Contact
              </Button>
              <div className="border-t border-gray-200/50 dark:border-gray-700/50 my-2"></div>

              {isSignedIn ? (
                <div className="flex flex-col items-center py-2 space-y-1">
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={() => {
                      void handleLogout();
                      toggleMobileMenu();
                    }}
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </Button>
                </div>
              ) : (
                <Button
                  variant="default"
                  className="w-full justify-center text-sm font-medium"
                  onMouseDown={() => {
                    navigate("/login");
                    toggleMobileMenu();
                  }}
                >
                  <User className="h-4 w-4" />
                  Sign in
                </Button>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
