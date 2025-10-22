import { Helmet } from 'react-helmet-async';

interface SEOHeadProps {
  title?: string;
  description?: string;
  image?: string;
  url?: string;
  type?: 'website' | 'article';
  keywords?: string[];
  author?: string;
  publishedTime?: string;
  modifiedTime?: string;
  section?: string;
  tags?: string[];
}

export const SEOHead = ({
  title = 'Wat2Do - Discover University of Waterloo Club Events',
  description = 'Find and explore exciting club events at the University of Waterloo. Browse upcoming events, discover campus clubs, and stay connected with the UW community through our comprehensive event discovery platform.',
  image = 'https://wat2do.ca/wat2do-logo.svg',
  url = 'https://wat2do.ca',
  type = 'website',
  keywords = [
    'University of Waterloo',
    'UW events',
    'campus clubs',
    'student events',
    'Waterloo university',
    'club directory',
    'event discovery',
    'UW community',
    'student life',
    'campus activities'
  ],
  author = 'Wat2Do',
  publishedTime,
  modifiedTime,
  section,
  tags = []
}: SEOHeadProps) => {
  const fullTitle = title.includes('Wat2Do') ? title : `${title} | Wat2Do`;
  const fullUrl = url.startsWith('http') ? url : `https://wat2do.ca${url}`;
  const fullImage = image.startsWith('http') ? image : `https://wat2do.ca${image}`;

  const structuredData = {
    "@context": "https://schema.org",
    "@type": type === 'article' ? "Article" : "WebSite",
    "name": fullTitle,
    "description": description,
    "url": fullUrl,
    "image": fullImage,
    "author": {
      "@type": "Organization",
      "name": author
    },
    "publisher": {
      "@type": "Organization",
      "name": "Wat2Do",
      "url": "https://wat2do.ca",
      "logo": {
        "@type": "ImageObject",
        "url": "https://wat2do.ca/wat2do-logo.svg"
      }
    },
    ...(type === 'article' && publishedTime && {
      "datePublished": publishedTime,
      "dateModified": modifiedTime || publishedTime
    }),
    ...(section && { "articleSection": section }),
    ...(tags.length > 0 && { "keywords": tags.join(", ") })
  };

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords.join(', ')} />
      <meta name="author" content={author} />
      <meta name="robots" content="index, follow" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="theme-color" content="#3B82F6" />
      
      {/* Canonical URL */}
      <link rel="canonical" href={fullUrl} />
      
      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={fullImage} />
      <meta property="og:url" content={fullUrl} />
      <meta property="og:site_name" content="Wat2Do" />
      <meta property="og:locale" content="en_CA" />
      
      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={fullImage} />
      <meta name="twitter:site" content="@wat2do_ca" />
      <meta name="twitter:creator" content="@wat2do_ca" />
      
      {/* Additional Meta Tags */}
      <meta name="application-name" content="Wat2Do" />
      <meta name="apple-mobile-web-app-title" content="Wat2Do" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="default" />
      
      {/* Favicon and Icons */}
      <link rel="icon" type="image/svg+xml" href="/wat2do-logo.svg" />
      <link rel="apple-touch-icon" href="/wat2do-logo.svg" />
      
      {/* Structured Data */}
      <script type="application/ld+json">
        {JSON.stringify(structuredData)}
      </script>
    </Helmet>
  );
};
