import EventBadgeMaskTopLeft from "@/assets/event-badge-svg-top-left.svg?react";
import EventBadgeMaskTopRight from "@/assets/event-badge-svg-top-right.svg?react";
import EventBadgeMaskBottomLeft from "@/assets/event-badge-svg-bottom-left.svg?react";
import EventBadgeMaskBottomRight from "@/assets/event-badge-svg-bottom-right.svg?react";

type BadgeMaskProps = {
  variant: "top-left" | "top-right" | "bottom-left" | "bottom-right";
  children: React.ReactNode;
};

function BadgeMask({ variant, children }: BadgeMaskProps) {
  switch (variant) {
    case "top-left":
      return (
        <div className="absolute top-0 left-0 flex flex-col">
          <div className="flex">
            <div className="pb-1 pr-1 bg-white dark:bg-gray-900 rounded-br-xl">{children}</div>
            <EventBadgeMaskTopLeft className="h-2 w-2 text-white dark:text-gray-900" />
          </div>
          <EventBadgeMaskTopLeft className="h-2 w-2 text-white dark:text-gray-900" />
        </div>
      );
    case "top-right":
      return (
        <div className="absolute top-0 right-0 flex flex-col">
          <div className="flex">
            <EventBadgeMaskTopRight className="h-2 w-2 text-white dark:text-gray-900" />
            <div className="pb-1 pl-1 bg-white dark:bg-gray-900 rounded-bl-xl">{children}</div>
          </div>
          <EventBadgeMaskTopRight className="h-2 w-2 ml-auto text-white dark:text-gray-900" />
        </div>
      );
    case "bottom-left":
      return (
        <div className="absolute bottom-0 left-0 flex flex-col">
          <EventBadgeMaskBottomLeft className="h-2 w-2 text-white dark:text-gray-900" />
          <div className="flex">
            <div className="pt-1 pr-1 bg-white dark:bg-gray-900 rounded-tr-xl">{children}</div>
            <EventBadgeMaskBottomLeft className="h-2 w-2 mt-auto text-white dark:text-gray-900" />
          </div>
        </div>
      );
    case "bottom-right":
      return (
        <div className="absolute bottom-0 right-0 flex flex-col">
          <div className="flex">
            <EventBadgeMaskBottomRight className="h-2 w-2 text-white dark:text-gray-900" />
            <div className="pb-1 pr-1 bg-white dark:bg-gray-900 rounded-br-xl">{children}</div>
          </div>
          <EventBadgeMaskBottomRight className="h-2 w-2 ml-auto text-white dark:text-gray-900" />
        </div>
      );
    default:
      return null;
  }
}

export default BadgeMask;
