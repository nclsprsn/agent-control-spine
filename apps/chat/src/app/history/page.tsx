import { useTranslations } from "next-intl";

export default function HistoryPage() {
  const t = useTranslations("history");

  return (
    <div className="p-6">
      <h1 className="text-lg font-medium mb-4">{t("title")}</h1>
      <p className="text-muted text-sm">{t("empty")}</p>
    </div>
  );
}
