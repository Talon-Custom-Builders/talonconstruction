/**
 * Cloudflare Pages Function — runs on every request.
 *
 * Canonical host is the apex domain: talonconstructioncompany.com.
 * Cloudflare Pages _redirects does not support domain-level (absolute-URL)
 * redirects, so this collapses the www subdomain and the project's default
 * *.pages.dev domain into the apex with a 301, in code instead.
 */

const CANONICAL_HOST = "talonconstructioncompany.com";

export async function onRequest(context) {
  const url = new URL(context.request.url);
  const { hostname } = url;

  const shouldRedirect =
    hostname === `www.${CANONICAL_HOST}` || hostname.endsWith(".pages.dev");

  if (shouldRedirect) {
    url.hostname = CANONICAL_HOST;
    url.protocol = "https:";
    return Response.redirect(url.toString(), 301);
  }

  return context.next();
}
