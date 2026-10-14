import { describe, expect, it } from "vitest";

import { getApiErrorMessage } from "./errors";

describe("getApiErrorMessage", () => {
  it("returns the string detail when the API sends a plain message", () => {
    const error = { response: { data: { detail: "Invalid credentials." } } };
    expect(getApiErrorMessage(error, "Fallback")).toBe("Invalid credentials.");
  });

  it("joins FastAPI validation errors into one readable sentence", () => {
    const error = {
      response: {
        data: {
          detail: [
            {
              type: "string_too_short",
              loc: ["body", "password"],
              msg: "String should have at least 6 characters",
            },
            { loc: ["body", "email"], msg: "field required" },
          ],
        },
      },
    };

    expect(getApiErrorMessage(error, "Fallback")).toBe(
      "Password: String should have at least 6 characters Email: field required",
    );
  });

  it("humanizes multi-word field names from the error location", () => {
    const error = {
      response: { data: { detail: [{ loc: ["body", "requested_amount"], msg: "must be positive" }] } },
    };

    expect(getApiErrorMessage(error, "Fallback")).toBe("Requested amount: must be positive");
  });

  it("supports the detailed object error shape", () => {
    const error = { response: { data: { detail: { message: "Scoring unavailable" } } } };
    expect(getApiErrorMessage(error, "Fallback")).toBe("Scoring unavailable");
  });

  it("falls back when the error payload is unusable", () => {
    expect(getApiErrorMessage({}, "Something went wrong")).toBe("Something went wrong");
    expect(getApiErrorMessage({ response: { data: {} } }, "Something went wrong")).toBe(
      "Something went wrong",
    );
    expect(getApiErrorMessage({ response: { data: { detail: [] } } }, "Something went wrong")).toBe(
      "Something went wrong",
    );
    expect(getApiErrorMessage({ response: { data: { detail: "   " } } }, "Fallback")).toBe("Fallback");
  });

  it("ignores non-string detail and unusable array entries", () => {
    const error = { response: { data: { detail: [42, null, { loc: [], msg: "boom" }] } } };
    expect(getApiErrorMessage(error, "Fallback")).toBe("boom");
  });
});
