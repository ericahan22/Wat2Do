import React from "react";
import { X } from "lucide-react";
import { IconButton } from "@/shared/components/ui/icon-button";
import { formatEventDate } from "@/shared/lib/dateUtils";
import { useLocalStorage } from "react-use";

function TopBanner() {
  const [isVisible, setIsVisible] = useLocalStorage("topBannerVisible", true);

  if (!isVisible) return null;

  return (
    <div className="w-full bg-[#0488FE]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-1.5 relative flex items-center justify-center">
        <a
          href="https://uwaterloo.ca/campus-status/"
          target="_blank" 
          rel="noopener noreferrer"
          className="hover:text-gray-200 cursor-pointer flex items-center"
        >
          <span className="text-sm font-small text-center !text-white">
            {formatEventDate("2026-01-26")} - UW campuses are closed today - all scheduled events are cancelled!
          </span>
        </a>
        <IconButton
          aria-label="Close banner"
          variant="ghost"
          size="icon"
          className="text-white absolute right-0"
          icon={X}
          onClick={() => setIsVisible(false)}
        />
      </div>
    </div>
  );
}

export default React.memo(TopBanner);
