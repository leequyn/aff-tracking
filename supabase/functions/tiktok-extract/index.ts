import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function cleanTitle(raw: string): string {
  return raw
    .replace(/\s*[\|–\-]\s*TikTok\s*$/i, "")
    .replace(/\s*[\|–\-]\s*TikTok Shop\s*$/i, "")
    .replace(/^TikTok Shop\s*[\|–\-]\s*/i, "")
    .trim();
}

function extractProductId(url: string): string | null {
  const m =
    url.match(/\/product\/(\d{10,})/i) ||
    url.match(/item_id=(\d{10,})/i) ||
    url.match(/product_id=(\d{10,})/i);
  return m ? m[1] : null;
}

function parseOgInfo(url: string): { title?: string; image?: string } | null {
  try {
    const og = new URL(url).searchParams.get("og_info");
    if (!og) return null;
    const d = JSON.parse(og);
    return {
      title: d.title?.trim() || undefined,
      image: d.image?.trim() || undefined,
    };
  } catch (_) {
    return null;
  }
}

function parseHtml(html: string): { title?: string; image?: string } {
  // og:title
  const ogTitle =
    html.match(/property=["']og:title["'][^>]*content=["']([^"']+)["']/i)?.[1] ||
    html.match(/content=["']([^"']+)["'][^>]*property=["']og:title["']/i)?.[1];

  // twitter:title
  const twTitle =
    html.match(/name=["']twitter:title["'][^>]*content=["']([^"']+)["']/i)?.[1] ||
    html.match(/content=["']([^"']+)["'][^>]*name=["']twitter:title["']/i)?.[1];

  // <title>
  const rawTitle = html.match(/<title>([^<]+)<\/title>/i)?.[1];

  // og:image
  const ogImage =
    html.match(/property=["']og:image["'][^>]*content=["'](https?:\/\/[^"']+)["']/i)?.[1] ||
    html.match(/content=["'](https?:\/\/[^"']+)["'][^>]*property=["']og:image["']/i)?.[1];

  const BAD = ["Security Check", "TikTok Shop", "TikTok", "Verify to continue", ""];
  const titleRaw = ogTitle || twTitle || rawTitle || "";
  const title = cleanTitle(titleRaw);
  const image = ogImage && !ogImage.includes("favicon") && !ogImage.includes("tts-logo")
    ? ogImage : undefined;

  return {
    title: title && !BAD.includes(title) ? title : undefined,
    image,
  };
}

// ── Case 1: shop.tiktok.com ───────────────────────────────────────────────────
async function fetchShopApi(productId: string): Promise<{ title?: string; image?: string } | null> {
  const UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) TikTok/30.4.0 Mobile/15E148 Safari/604.1";

  const endpoints = [
    `https://shop.tiktok.com/api/v2/product/detail?product_id=${productId}`,
    `https://shop.tiktok.com/api/v1/product/detail?product_id=${productId}`,
    `https://shop.tiktok.com/view/product/${productId}?ajax=1`,
  ];

  for (const url of endpoints) {
    try {
      const resp = await fetch(url, {
        headers: {
          "User-Agent": UA,
          "Accept": "application/json, text/plain, */*",
          "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
          "Referer": "https://shop.tiktok.com/",
          "Origin": "https://shop.tiktok.com",
          "X-Requested-With": "XMLHttpRequest",
          "X-TT-Request-Tag": "shop",
        },
      });
      if (!resp.ok) continue;
      const ct = resp.headers.get("content-type") ?? "";
      if (!ct.includes("json")) continue;

      const data = await resp.json();
      const title =
        data?.data?.product?.title ||
        data?.data?.title ||
        data?.product?.title ||
        data?.result?.title ||
        data?.title ||
        data?.name ||
        data?.product_name;

      const image =
        data?.data?.product?.images?.[0]?.url_list?.[0] ||
        data?.data?.product?.images?.[0]?.url ||
        data?.product?.images?.[0]?.url ||
        data?.data?.cover_url ||
        data?.image;

      if (title) return { title: cleanTitle(title), image };
    } catch (_) { /* silent */ }
  }
  return null;
}

// ── Case 2: vt.tiktok.com / www.tiktok.com ───────────────────────────────────
async function fetchTiktokHtml(url: string): Promise<{ title?: string; image?: string } | null> {
  const UAS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
  ];

  for (const ua of UAS) {
    try {
      const resp = await fetch(url, {
        redirect: "follow",
        headers: {
          "User-Agent": ua,
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
          "Cache-Control": "no-cache",
        },
      });
      const html = await resp.text();
      const meta = parseHtml(html);
      if (meta.title || meta.image) return meta;
    } catch (_) { /* silent */ }
  }
  return null;
}

// ── Main ──────────────────────────────────────────────────────────────────────
serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: CORS });
  }

  try {
    const { url } = await req.json();
    if (!url) {
      return new Response(JSON.stringify({ error: "url required" }), {
        status: 400, headers: { ...CORS, "Content-Type": "application/json" },
      });
    }

    const parsed = new URL(url);
    const host = parsed.hostname;

    // ── Case 1: shop.tiktok.com ──
    if (host === "shop.tiktok.com") {
      const productId = extractProductId(url);
      if (productId) {
        const result = await fetchShopApi(productId);
        if (result?.title) {
          return new Response(JSON.stringify(result), {
            headers: { ...CORS, "Content-Type": "application/json" },
          });
        }
      }
    }

    // ── Case 2: vt.tiktok.com hoặc www.tiktok.com ──
    // Bước 1: resolve redirect → lấy full URL
    let finalUrl = url;
    try {
      const r = await fetch(url, {
        redirect: "follow",
        headers: { "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" },
      });
      finalUrl = r.url;
    } catch (_) { /* dùng url gốc */ }

    // Bước 2: thử lấy og_info từ URL params
    const ogInfo = parseOgInfo(finalUrl);
    if (ogInfo?.title) {
      return new Response(JSON.stringify(ogInfo), {
        headers: { ...CORS, "Content-Type": "application/json" },
      });
    }

    // Bước 3: nếu là shop product → thử API
    const productId = extractProductId(finalUrl);
    if (productId) {
      const apiResult = await fetchShopApi(productId);
      if (apiResult?.title) {
        return new Response(JSON.stringify(apiResult), {
          headers: { ...CORS, "Content-Type": "application/json" },
        });
      }
    }

    // Bước 4: fetch HTML + parse og:title → twitter:title → <title>
    const htmlResult = await fetchTiktokHtml(finalUrl);
    if (htmlResult?.title || htmlResult?.image) {
      return new Response(JSON.stringify(htmlResult ?? {}), {
        headers: { ...CORS, "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({ error: "Không lấy được dữ liệu từ link này" }), {
      status: 422,
      headers: { ...CORS, "Content-Type": "application/json" },
    });

  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), {
      status: 500,
      headers: { ...CORS, "Content-Type": "application/json" },
    });
  }
});
