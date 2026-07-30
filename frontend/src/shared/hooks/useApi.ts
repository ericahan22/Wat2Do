import { useMemo } from "react";
import BaseAPIClient, { getAccessToken } from "@/shared/api/BaseAPIClient";
import EventsAPIClient from "@/shared/api/EventsAPIClient";
import ClubsAPIClient from "@/shared/api/ClubsAPIClient";

export const useApi = () => {
  return useMemo(() => {
    const baseApiClient = new BaseAPIClient(async () => getAccessToken());
    const eventsAPIClient = new EventsAPIClient(baseApiClient);

    return {
      eventsAPIClient,
      clubsAPIClient: new ClubsAPIClient(baseApiClient),
    };
  }, []);
};
