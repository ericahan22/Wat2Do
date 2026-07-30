import { useState } from "react";
import { X, ExternalLink } from "lucide-react";

export function MigrationBanner() {
    const [isVisible, setIsVisible] = useState(true);

    if (!isVisible) return null;

    return (
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-2.5 text-center text-sm font-medium relative z-50 flex items-center justify-center shadow-md">
            <div className="flex items-center space-x-2">
                <span>We are moving to a new home! Check out our new platform at</span>
                <a
                    href="https://wat2do.io"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline font-bold hover:text-blue-200 inline-flex items-center gap-1"
                >
                    wat2do.io
                    <ExternalLink className="h-3 w-3" />
                </a>
            </div>
            <button
                onClick={() => setIsVisible(false)}
                className="absolute right-4 p-1 rounded-full hover:bg-white/20 transition-colors"
                aria-label="Close banner"
            >
                <X className="h-4 w-4" />
            </button>
        </div>
    );
}