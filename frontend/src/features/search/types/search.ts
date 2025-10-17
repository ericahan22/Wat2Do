export interface SearchState {
  query: string;
  isActive: boolean;
}

export interface SearchFilters {
  category?: string;
  clubType?: string;
  dateRange?: {
    start: string;
    end: string;
  };
}
