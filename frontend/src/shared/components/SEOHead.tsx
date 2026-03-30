import React, { useEffect } from "react";

type Props = {
  title?: string;
  description?: string;
  url?: string;
  image?: string;
  keywords?: string[];
  children?: React.ReactNode;
};

function toAbsoluteUrl(value: string) {
  if (/^https?:\/\//i.test(value)) {
    return value;
  }

  const origin = window.location.origin;
  return new URL(value, origin).toString();
}

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
    const absoluteUrl = url ? toAbsoluteUrl(url) : undefined;
    const absoluteImage = image ? toAbsoluteUrl(image) : undefined;

    if (title) document.title = title;

    if (description) upsertMeta("name", "description", description);
    if (keywords && keywords.length > 0) upsertMeta("name", "keywords", keywords.join(", "));
    if (title) upsertMeta("property", "og:title", title);
    if (description) upsertMeta("property", "og:description", description);
    if (absoluteUrl) upsertMeta("property", "og:url", absoluteUrl);
    if (absoluteImage) upsertMeta("property", "og:image", absoluteImage);
    upsertMeta("name", "twitter:card", absoluteImage ? "summary_large_image" : "summary");

    // canonical link
    if (absoluteUrl) {
      let link = document.head.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
      if (!link) {
        link = document.createElement("link");
        link.setAttribute("rel", "canonical");
        document.head.appendChild(link);
      }
      link.setAttribute("href", absoluteUrl);
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
