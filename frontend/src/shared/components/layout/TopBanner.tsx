import React from "react";
import { X } from "lucide-react";
import { IconButton } from "@/shared/components/ui/icon-button";
import { formatEventDate } from "@/shared/lib/dateUtils";
import { useLocalStorage } from "react-use";

function TopBanner() {
  const [isVisible, setIsVisible] = useLocalStorage("topBannerVisible", true);

  if (!isVisible) return null;

  return (
    <div className="w-full !bg-[#0056D6]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-1.5 relative flex items-center justify-center">
        <a
          href="https://wat2do.instatus.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-gray-200"
        >
          <span className="text-sm font-small text-center !text-white">
            {formatEventDate("2025-11-06")} - Interested events now available!
          </span>
        </a>
        <IconButton
          aria-label="Close banner"
          variant="ghost"
          size="icon"
          className="text-white absolute right-0"
          icon={X}
          onMouseDown={() => setIsVisible(false)}
        />
      </div>
    </div>
  );
}

export default React.memo(TopBanner);
