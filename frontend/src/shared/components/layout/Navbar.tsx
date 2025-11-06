import { Moon, Sun, Menu, X, User, Settings, LogOut, LayoutDashboard } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { useNavbar } from "@/shared/hooks";
import { useAuth, UserButton, useClerk } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import { CLERK_ROUTES } from "@/shared/config/clerk";

function Navbar() {
  const {
    isMobileMenuOpen,
    theme,
    isActive,
    toggleMobileMenu,
    toggleTheme,
  } = useNavbar();
  const navigate = useNavigate();

  const { isSignedIn } = useAuth();
  const { signOut } = useClerk();

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
              {/* Auth Section */}
              {isSignedIn ? (
                <>
                  <Button
                    variant="ghost"
                    className="text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    onMouseDown={() => navigate(CLERK_ROUTES.DASHBOARD)}
                  >
                    <LayoutDashboard className="h-4 w-4" />
                    Dashboard
                  </Button>
                  <UserButton
                    appearance={{
                      elements: {
                        avatarBox: "h-9 w-9",
                      },
                    }}
                    afterSignOutUrl={CLERK_ROUTES.HOME}
                    userProfileMode="navigation"
                    userProfileUrl={CLERK_ROUTES.USER_PROFILE}
                  />
                </>
              ) : (
                <Button
                  variant="default"
                  className="text-sm font-medium"
                  onMouseDown={() => navigate(CLERK_ROUTES.SIGN_IN)}
                >
                  <User className="h-4 w-4" />
                  Sign in
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
              {isSignedIn ? (
                <div className="flex flex-col items-center py-3 space-y-3">
                  <div className="w-full space-y-1">
                    <Button
                      variant="ghost"
                      className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                      onMouseDown={() => {
                        navigate(CLERK_ROUTES.DASHBOARD);
                        toggleMobileMenu();
                      }}
                    >
                      <LayoutDashboard className="h-4 w-4" />
                      Dashboard
                    </Button>
                    <Button
                      variant="ghost"
                      className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                      onMouseDown={() => {
                        navigate(CLERK_ROUTES.USER_PROFILE);
                        toggleMobileMenu();
                      }}
                    >
                      <Settings className="h-4 w-4" />
                      Profile Settings
                    </Button>
                    <Button
                      variant="ghost"
                      className="w-full justify-start text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                      onMouseDown={() => signOut()}
                    >
                      <LogOut className="h-4 w-4" />
                      Sign Out
                    </Button>
                  </div>
                </div>
              ) : (
                <Button
                  variant="default"
                  className="w-full justify-center text-sm font-medium"
                  onMouseDown={() => {
                    navigate(CLERK_ROUTES.SIGN_IN);
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
