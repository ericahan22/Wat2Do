import React, { useEffect } from "react";

type Props = {
  title?: string;
  description?: string;
  url?: string;
  image?: string;
  keywords?: string[];
  children?: React.ReactNode;
};

function upsertMeta(attrName: "name" | "property", key: string, content: string) {
  if (!content) return;
  const selector = `meta[${attrName}="${key}"]`;
  let el = document.head.querySelector(selector) as HTMLMetaElement | null;
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attrName, key);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

function SEOHead({
  title,
  description,
  url,
  image,
  keywords,
  children,
}: Props) {
  useEffect(() => {
    const prevTitle = document.title;
    if (title) document.title = title;

    if (description) upsertMeta("name", "description", description);
    if (title) upsertMeta("property", "og:title", title);
    if (description) upsertMeta("property", "og:description", description);
    if (url) upsertMeta("property", "og:url", url);
    if (image) upsertMeta("property", "og:image", image);
    upsertMeta("name", "twitter:card", image ? "summary_large_image" : "summary");

    // canonical link
    if (url) {
      let link = document.head.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
      if (!link) {
        link = document.createElement("link");
        link.setAttribute("rel", "canonical");
        document.head.appendChild(link);
      }
      link.setAttribute("href", url);
    }

    return () => {
      // restore previous title only
      document.title = prevTitle;
      // keep meta tags (avoid removing other app meta); if you prefer cleanup, implement here
    };
  }, [title, description, url, image, keywords]);

  return <>{children ?? null}</>;
}

export default SEOHead;
export { SEOHead };
