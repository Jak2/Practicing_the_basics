import type { Metadata } from "next";

const SITE_NAME = "Outflo";
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://outflo.vercel.app";
const SITE_DESCRIPTION =
  "Outcome-driven AI workflows and prompts that solve real-world business problems.";

export function buildMetadata({
  title,
  description,
  image,
  path: urlPath = "/",
}: {
  title?: string;
  description?: string;
  image?: string;
  path?: string;
}): Metadata {
  const fullTitle = title ? `${title} | ${SITE_NAME}` : SITE_NAME;
  const desc = description ?? SITE_DESCRIPTION;
  const url = `${SITE_URL}${urlPath}`;
  const ogImage = image || `${SITE_URL}/og-default.png`;

  return {
    title: fullTitle,
    description: desc,
    metadataBase: new URL(SITE_URL),
    openGraph: {
      title: fullTitle,
      description: desc,
      url,
      siteName: SITE_NAME,
      images: [{ url: ogImage }],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: fullTitle,
      description: desc,
      images: [ogImage],
    },
    alternates: { canonical: url },
  };
}
