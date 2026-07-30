import type { Club } from "@/features/clubs/types/clubs";
import BaseAPIClient from "@/shared/api/BaseAPIClient";

export interface ClubsResponse {
  results: Club[];
  nextCursor: string | null;
  hasMore: boolean;
  totalCount: number;
}

export interface ClubsQueryParams {
  search?: string;
  category?: string;
  cursor?: string;
  school?: string;
}

interface ApiOrganization {
  id: number;
  organization_name: string;
  categories?: string[] | null;
  organization_page?: string | null;
  ig?: string | null;
  discord?: string | null;
  organization_type?: string | null;
  logo_url?: string | null;
  school?: string | null;
}

interface ApiOrganizationFeed {
  items: ApiOrganization[];
  total: number;
  page: number;
  total_pages: number;
}

function instagramUsername(value?: string | null): string {
  if (!value) return "";
  try {
    const url = new URL(value);
    if (!url.hostname.includes("instagram.com")) return "";
    return url.pathname.split("/").filter(Boolean)[0] ?? "";
  } catch {
    return value.replace(/^@/, "");
  }
}

function normalizeOrganization(organization: ApiOrganization): Club {
  return {
    id: organization.id,
    club_name: organization.organization_name,
    categories: organization.categories ?? [],
    club_page: organization.organization_page ?? "",
    ig: instagramUsername(organization.ig),
    discord: organization.discord ?? "",
    club_type: organization.organization_type ?? "",
    logo_url: organization.logo_url ?? null,
    school: organization.school ?? null,
  };
}

class ClubsAPIClient {
  constructor(private apiClient: BaseAPIClient) {}

  async getClubs(params: ClubsQueryParams = {}): Promise<ClubsResponse> {
    const searchParams = new URLSearchParams({
      page: params.cursor || "1",
      page_size: "100",
    });
    if (params.school) searchParams.set("school", params.school);
    if (params.search) searchParams.set("search", params.search);
    if (params.category && params.category !== "all") {
      searchParams.append("categories", params.category);
    }

    const feed = await this.apiClient.get<ApiOrganizationFeed>(
      `organizations/?${searchParams.toString()}`,
    );
    const hasMore = feed.page < feed.total_pages;

    return {
      results: feed.items.map(normalizeOrganization),
      nextCursor: hasMore ? String(feed.page + 1) : null,
      hasMore,
      totalCount: feed.total,
    };
  }
}

export default ClubsAPIClient;
