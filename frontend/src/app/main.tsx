import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { ThemeProvider } from "@/shared/lib/theme";
import { ClerkAppProvider } from "@/shared/components/ClerkAppProvider";
import "@/app/index.css";
import App from "@/app/App.tsx";
import { BrowserRouter } from "react-router-dom";
import { SEOHead } from "@/shared";
import { Analytics } from "@vercel/analytics/react";
import { Toaster } from "@/components/ui/sonner";
import { handleError } from "@/shared/lib/errorHandler";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5,
    },
    mutations: {},
  },
  queryCache: new QueryCache({
    onError: (error, query) => {
      if (query.meta?.skipErrorToast) return;
      handleError(error);
    },
  }),
  mutationCache: new MutationCache({
    onError: (error, _vars, _ctx, mutation) => {
      if (mutation.meta?.skipErrorToast) return;
      handleError(error);
    },
  }),
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <ClerkAppProvider>
          <QueryClientProvider client={queryClient}>
            <SEOHead />
            <Analytics />
            <App />
            <Toaster />
          </QueryClientProvider>
        </ClerkAppProvider>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>
);
