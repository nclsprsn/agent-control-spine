const PROMETHEUS_URL =
  process.env.PROMETHEUS_URL || "http://localhost:9090";

export async function promQuery(query: string): Promise<number | null> {
  try {
    const url = `${PROMETHEUS_URL}/api/v1/query?query=${encodeURIComponent(query)}`;
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return null;
    const json = (await res.json()) as {
      status: string;
      data: { result: { value: [number, string] }[] };
    };
    if (json.status !== "success" || json.data.result.length === 0) return null;
    const raw = parseFloat(json.data.result[0].value[1]);
    return isFinite(raw) ? raw : null;
  } catch {
    return null;
  }
}
