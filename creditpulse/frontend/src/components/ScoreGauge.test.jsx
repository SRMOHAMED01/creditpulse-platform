import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ScoreGauge from "./ScoreGauge";

describe("ScoreGauge", () => {
  it("renders the score the caller provides", () => {
    render(<ScoreGauge score={82} />);
    expect(screen.getByText("82")).toBeInTheDocument();
    expect(screen.getByText("Score Out of 100")).toBeInTheDocument();
  });

  it("defaults to 0 when no score is provided", () => {
    render(<ScoreGauge />);
    expect(screen.getByText("0")).toBeInTheDocument();
  });

  it("clamps scores outside the 0-100 range", () => {
    const { rerender } = render(<ScoreGauge score={140} />);
    expect(screen.getByText("100")).toBeInTheDocument();

    rerender(<ScoreGauge score={-25} />);
    expect(screen.getByText("0")).toBeInTheDocument();
  });

  it("coerces non-numeric input safely to 0", () => {
    render(<ScoreGauge score="not-a-number" />);
    expect(screen.getByText("0")).toBeInTheDocument();
  });

  it("renders the conic gradient that visualises the score", () => {
    const { container } = render(<ScoreGauge score={50} />);
    const arc = container.querySelector(".score-arc-container");
    expect(arc).not.toBeNull();
    expect(arc.style.background).toContain("conic-gradient");
    expect(arc.style.background).toContain("180deg");
  });
});
