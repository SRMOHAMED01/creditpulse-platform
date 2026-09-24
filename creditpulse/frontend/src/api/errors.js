const humanizeField = (value) =>
  String(value || "field")
    .replaceAll("_", " ")
    .replace(/^./, (letter) => letter.toUpperCase());

export function getApiErrorMessage(error, fallback) {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (!item || typeof item !== "object") return null;

        const field = Array.isArray(item.loc) ? item.loc.at(-1) : null;
        const message = typeof item.msg === "string" ? item.msg : null;
        if (!message) return null;
        return field ? `${humanizeField(field)}: ${message}` : message;
      })
      .filter(Boolean);

    if (messages.length) return messages.join(" ");
  }

  if (detail && typeof detail === "object" && typeof detail.message === "string") {
    return detail.message;
  }

  return fallback;
}
