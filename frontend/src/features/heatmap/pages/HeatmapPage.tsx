import React from "react";
import HeatMap from "@uiw/react-heat-map";

// Generate random static data for Sept 1 - Dec 30, 2025
const generateHeatmapData = () => {
  const data: { date: string; count: number }[] = [];
  const startDate = new Date(2025, 8, 1); // Sept 1, 2025
  const endDate = new Date(2025, 11, 30); // Dec 30, 2025

  // Seed for reproducible "random" data
  let seed = 42;
  const random = () => {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };

  const current = new Date(startDate);
  while (current <= endDate) {
    const year = current.getFullYear();
    const month = String(current.getMonth() + 1).padStart(2, "0");
    const day = String(current.getDate()).padStart(2, "0");
    const dateStr = `${year}/${month}/${day}`;

    // Random count 0-20
    const count = Math.floor(random() * 21);
    data.push({ date: dateStr, count });

    current.setDate(current.getDate() + 1);
  }

  return data;
};

const heatmapData = generateHeatmapData();

const HeatmapPage: React.FC = () => {
  return (
    <div className="min-h-screen">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold mb-8 text-gray-900 dark:text-gray-100">
          Contribution Heatmap
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          September 1 - December 30, 2025
        </p>

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-6 overflow-x-auto">
          <HeatMap
            value={heatmapData}
            startDate={new Date("2025/09/01")}
            endDate={new Date("2025/12/30")}
            width={700}
            weekLabels={["", "Mon", "", "Wed", "", "Fri", ""]}
            panelColors={[
              "#ebedf0",
              "#9be9a8",
              "#40c463",
              "#30a14e",
              "#216e39",
            ]}
            rectProps={{ rx: 2 }}
          />
        </div>
      </div>
    </div>
  );
};

export default HeatmapPage;
