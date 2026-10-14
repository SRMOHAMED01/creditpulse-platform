import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("api client", () => {
  const originalLocation = window.location;

  const setLocation = (href = "http://localhost:5173/dashboard") => {
    const url = new URL(href);
    Object.defineProperty(window, "location", {
      configurable: true,
      value: {
        ...url,
        assign: vi.fn(),
        get href() {
          return url.href;
        },
      },
    });
  };

  const loadClient = async () => {
    vi.resetModules();
    return (await import("./client")).default;
  };

  beforeEach(() => {
    localStorage.clear();
    setLocation();
  });

  afterEach(() => {
    Object.defineProperty(window, "location", {
      configurable: true,
      value: originalLocation,
    });
    vi.restoreAllMocks();
  });

  it("attaches the stored bearer token to outgoing requests", async () => {
    localStorage.setItem("creditpulse_token", "test-token");
    const client = await loadClient();

    const request = client.interceptors.request;
    const config = request.handlers[0].fulfilled({ headers: {} });
    expect(config.headers.Authorization).toBe("Bearer test-token");
  });

  it("does not attach an Authorization header when no token is stored", async () => {
    const client = await loadClient();
    const request = client.interceptors.request;
    const config = request.handlers[0].fulfilled({ headers: {} });
    expect(config.headers.Authorization).toBeUndefined();
  });

  it("clears the token and redirects to login on a 401 response", async () => {
    localStorage.setItem("creditpulse_token", "stale-token");
    const client = await loadClient();

    const error = { response: { status: 401 } };
    await expect(
      client.interceptors.response.handlers[0].rejected(error),
    ).rejects.toEqual(error);

    expect(localStorage.getItem("creditpulse_token")).toBeNull();
    expect(window.location.assign).toHaveBeenCalledWith("/login");
  });

  it("passes non-401 errors through untouched", async () => {
    localStorage.setItem("creditpulse_token", "still-valid");
    const client = await loadClient();

    const error = { response: { status: 500 } };
    await expect(
      client.interceptors.response.handlers[0].rejected(error),
    ).rejects.toEqual(error);

    expect(localStorage.getItem("creditpulse_token")).toBe("still-valid");
    expect(window.location.assign).not.toHaveBeenCalled();
  });

  it("uses the configured API base URL", async () => {
    const client = await loadClient();
    expect(client.defaults.baseURL).toBe("http://localhost:8000");
  });
});
