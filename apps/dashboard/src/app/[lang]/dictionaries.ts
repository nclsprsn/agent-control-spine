import "server-only";
import type { Locale } from "@/middleware";

const dictionaries = {
  en: () =>
    import("../../../dictionaries/en.json").then((m) => m.default),
  fr: () =>
    import("../../../dictionaries/fr.json").then((m) => m.default),
};

export type Dictionary = Awaited<ReturnType<typeof getDictionary>>;

export const getDictionary = async (locale: Locale) =>
  dictionaries[locale]();
