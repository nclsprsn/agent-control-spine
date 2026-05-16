import { getRequestConfig } from "next-intl/server";
import { headers } from "next/headers";

export default getRequestConfig(async () => {
  const h = await headers();
  const acceptLang = h.get("accept-language") ?? "";
  const locale = acceptLang.startsWith("fr") ? "fr" : "en";

  const messages = (await import(`../../messages/${locale}.json`)).default;

  return { locale, messages };
});
