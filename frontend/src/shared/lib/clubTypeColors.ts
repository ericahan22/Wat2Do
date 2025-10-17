export interface ClubTypeColor {
  backgroundColor: string;
  name: string;
}

export const clubTypeColors: Record<string, ClubTypeColor> = {
  "WUSA": {
    backgroundColor: "#4b9b6a",
    name: "WUSA Club Events"
  },
  "Athletics": {
    backgroundColor: "#d9924a", 
    name: "Athletics Events"
  },
  "Student Society": {
    backgroundColor: "#d16c6c",
    name: "Student Society Events"
  },
  "default": {
    backgroundColor: "#3a7bd5",
    name: "Other Events"
  }
};

export const getClubTypeColor = (clubType?: string | null): string => {
  if (!clubType || !clubTypeColors[clubType]) {
    return clubTypeColors.default.backgroundColor;
  }
  return clubTypeColors[clubType].backgroundColor;
};

export const getAllClubTypes = (): ClubTypeColor[] => {
  return Object.entries(clubTypeColors)
    .filter(([key]) => key !== "default")
    .map(([, value]) => value)
    .concat([clubTypeColors.default]); // Add default at the end
};
