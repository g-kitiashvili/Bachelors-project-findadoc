/**
 * Append a comma-joined UI value as repeated query params (`key=a&key=b`) so the API
 * binds it to a `List<String>`. The page URLs keep the compact comma form; only the
 * outgoing API call is expanded into repeated params.
 */
export function appendList(target: URLSearchParams, key: string, csv: string | null | undefined): void {
  (csv ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
    .forEach((v) => target.append(key, v));
}
