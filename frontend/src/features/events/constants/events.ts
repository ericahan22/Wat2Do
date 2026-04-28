export const EVENTS_PER_PAGE = 24;

export const SCHOOLS = [
  { value: "University of Waterloo", label: "Waterloo" },
  { value: "University of Pennsylvania", label: "UPenn" },
  { value: "New York University", label: "NYU" },
  { value: "Columbia University", label: "Columbia" },
  { value: "Massachusetts Institute of Technology", label: "MIT" },
] as const;

export const DEFAULT_SCHOOL = SCHOOLS[0].value;
