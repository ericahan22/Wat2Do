import React from "react";
import { X } from "lucide-react";
import { IconButton } from "@/shared/components/ui/icon-button";
import { useLocalStorage } from "react-use";

function TopBanner() {
  const [isVisible, setIsVisible] = useLocalStorage("topBannerVisible", true);

  if (!isVisible) return null;

  return (
    <div className="w-full bg-[#0488FE]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-1.5 relative flex items-center justify-center">
        <span className="text-sm font-small text-center !text-white">
          Wat2Do will be under maintenance this weekend (June 12–14), from 8 PM
          Friday to 8 PM Sunday.
        </span>
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
