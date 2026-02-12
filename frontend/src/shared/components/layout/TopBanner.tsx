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
        <a
          href="https://status.supabase.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-gray-200 cursor-pointer"
        >
          <span className="text-sm font-small text-center !text-white">
            February 12, 2026: App is down due to Supabase. Learn more
            https://status.supabase.com/
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
