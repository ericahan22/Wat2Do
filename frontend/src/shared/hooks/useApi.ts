// src/hooks/useApi.js
import { useMemo } from 'react';
import { useAuth } from '@clerk/clerk-react';

import BaseAPIClient from '@/shared/api/BaseAPIClient';
import EventsAPIClient from '@/shared/api/EventsAPIClient';
import NewsletterAPIClient from '@/shared/api/NewsletterAPIClient';
import ClubsAPIClient from '@/shared/api/ClubsAPIClient';
import AdminAPIClient from '@/shared/api/AdminAPIClient';

export const useApi = () => {
  const { getToken } = useAuth();

  // useMemo ensures we don't create new instances on every render
  const apiClients = useMemo(() => {
    // Pass a function that calls getToken. This ensures a fresh token is
    // fetched for every request.
    const baseApiClient = new BaseAPIClient(() => getToken());

    return {
      events: new EventsAPIClient(baseApiClient),
      newsletter: new NewsletterAPIClient(baseApiClient),
      clubs: new ClubsAPIClient(baseApiClient),
      admin: new AdminAPIClient(baseApiClient),
    };
  }, [getToken]);

  return apiClients;
};
