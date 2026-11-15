import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Button, ErrorState, Status } from "./ui";
import { sampleSchema } from "../schema";
describe("shared UI and validation", () => {
  it("runs retry only when clicked", () => {
    const retry = vi.fn();
    render(<ErrorState error={new Error("Backend offline")} retry={retry} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Backend offline");
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(retry).toHaveBeenCalledOnce();
  });
  it("pairs status color with readable text", () => {
    render(<Status status="unknown" />);
    expect(screen.getByText("Unverified")).toBeVisible();
  });
  it("prevents actions while disabled", () => {
    const click = vi.fn();
    render(
      <Button disabled onClick={click}>
        Analyze Sample
      </Button>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Analyze Sample" }));
    expect(click).not.toHaveBeenCalled();
  });
  it("rejects missing, nonfinite and out-of-range measurements", () => {
    const sample = {
      ph: 7,
      Hardness: 200,
      Solids: 20000,
      Chloramines: 7,
      Sulfate: 300,
      Conductivity: 450,
      Organic_carbon: 14,
      Trihalomethanes: 60,
      Turbidity: 4,
    };
    expect(sampleSchema.safeParse(sample).success).toBe(true);
    for (const patch of [
      { ph: 15 },
      { ph: NaN },
      { Hardness: -1 },
      { Turbidity: Infinity },
    ])
      expect(sampleSchema.safeParse({ ...sample, ...patch }).success).toBe(
        false,
      );
    expect(sampleSchema.safeParse({}).success).toBe(false);
  });
});
