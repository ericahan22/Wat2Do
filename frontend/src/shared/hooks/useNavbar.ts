import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useTheme } from "./useTheme";

export const useNavbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (path: string) => {
    return (
      location.pathname === path ||
      (path === "/events" && location.pathname === "/")
    );
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    closeMobileMenu();
  };

  return {
    // State
    isMobileMenuOpen,
    theme,
    
    isActive,
    toggleMobileMenu,
    closeMobileMenu,
    handleNavigation,
    toggleTheme,
  };
};
