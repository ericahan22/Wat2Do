import React from "react";
import { getAllClubTypes } from "@/shared/lib/clubTypeColors";

const EventLegend: React.FC = () => {
  const clubTypes = getAllClubTypes();

  return (
    <div className="flex flex-wrap items-center justify-center gap-6 mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-md">
      {clubTypes.map((clubType, index) => (
        <div key={index} className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: clubType.backgroundColor }}
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">
            {clubType.name}
          </span>
        </div>
      ))}
    </div>
  );
};

export default EventLegend;
