// import { useMemo } from "react";
// import { useSearchParams } from "react-router-dom";
// import { Event } from "./useEvents";
// import { staticEventsData } from "@/data/staticEvents";

// export function useStaticEvents(view: "grid" | "calendar") {
//   const [searchParams] = useSearchParams();
//   const searchTerm = searchParams.get("search") || "";
//   const categoryFilter = searchParams.get("category") || "all";

//   // Filter the static data based on search params
//   const filteredData = useMemo(() => {
//     let filtered = [...staticEventsData];

//     // Apply search filter
//     if (searchTerm) {
//       const searchLower = searchTerm.toLowerCase();
//       filtered = filtered.filter(
//         (event) =>
//           event.name.toLowerCase().includes(searchLower) ||
//           event.location.toLowerCase().includes(searchLower) ||
//           event.club_handle.toLowerCase().includes(searchLower) ||
//           (event.food && event.food.toLowerCase().includes(searchLower))
//       );
//     }

//     // Apply category filter
//     if (categoryFilter && categoryFilter !== "all") {
//       filtered = filtered.filter((event) =>
//         event.categories?.includes(categoryFilter)
//       );
//     }

//     return filtered;
//   }, [searchTerm, categoryFilter]);

//   const uniqueCategories = useMemo(() => {
//     return [
//       "Academic",
//       "Athletics",
//       "Business and Entrepreneurial",
//       "Charitable, Community Service & International Development",
//       "Creative Arts, Dance and Music",
//       "Cultural",
//       "Environmental and Sustainability",
//       "Games, Recreational and Social",
//       "Health Promotion",
//       "Media, Publications and Web Development",
//       "Political and Social Awareness",
//       "Religious and Spiritual",
//     ];
//   }, []);

//   return {
//     data: filteredData,
//     uniqueCategories,
//     isLoading: false, // Static data is always loaded
//     error: null, // No errors with static data
//   };
// }
