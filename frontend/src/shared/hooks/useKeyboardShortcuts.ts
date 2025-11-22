import { useEffect, useCallback } from "react";

interface UseKeyboardShortcutsProps {
    onSlash?: () => void;
    onEscape?: () => void;
}

export function useKeyboardShortcuts({ onSlash, onEscape }: UseKeyboardShortcutsProps) {
    const handleKeyDown = useCallback(
        (event: KeyboardEvent) => {
            // Don't trigger shortcuts if user is typing in an input/textarea
            const target = event.target as HTMLElement;
            const isTyping =
                target.tagName === "INPUT" ||
                target.tagName === "TEXTAREA" ||
                target.isContentEditable;

            // Slash to focus search (only when not already typing)
            if (event.key === "/" && !isTyping && onSlash) {
                event.preventDefault();
                onSlash();
            }

            // Escape to clear search (works even when typing in search)
            if (event.key === "Escape" && onEscape) {
                onEscape();
            }
        },
        [onSlash, onEscape]
    );

    useEffect(() => {
        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [handleKeyDown]);
}
