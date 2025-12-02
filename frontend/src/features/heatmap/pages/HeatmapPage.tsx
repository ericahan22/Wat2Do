import React, { useState, useEffect } from "react";
import HeatMap from "@uiw/react-heat-map";
import { useApi } from "@/shared/hooks/useApi";
import type { HeatmapDataPoint } from "@/shared/api/EventsAPIClient";

const HeatmapPage: React.FC = () => {
  const startDate = new Date("2025/09/01");
  const endDate = new Date("2025/12/30");

  const [heatmapData, setHeatmapData] = useState<HeatmapDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { eventsAPIClient } = useApi();

  useEffect(() => {
    const fetchEventHeatmap = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // 1. Fetch data from the new backend API endpoint
        // Pass dates in YYYY-MM-DD format as expected by backend
        const response = await eventsAPIClient.getHeatmapData({
          start_date: startDate.toISOString().split('T')[0],
          end_date: endDate.toISOString().split('T')[0]
        });

        // 2. Format the data for the HeatMap component
        const formattedData: HeatmapDataPoint[] = response.data.map(item => ({
          // The component expects "YYYY/MM/DD", so replace '-' with '/'
          date: item.date.replace(/-/g, '/'),
          count: item.count,
        }));

        setHeatmapData(formattedData);
      } catch (err) {
        console.error("Failed to fetch heatmap data:", err);
        setError("Failed to load event data. Please check the API endpoint.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchEventHeatmap();
  }, [eventsAPIClient]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-xl text-gray-600 dark:text-gray-400">Loading real event data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-xl text-red-500">{error}</p>
      </div>
    );
  }

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
            startDate={startDate}
            endDate={endDate}
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