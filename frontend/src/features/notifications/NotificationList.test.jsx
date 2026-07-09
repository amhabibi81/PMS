import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastProvider } from "../../contexts/ToastContext";
import NotificationList from "./NotificationList";

function renderList() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <ToastProvider>
        <NotificationList />
      </ToastProvider>
    </QueryClientProvider>
  );
}

describe("NotificationList", () => {
  beforeEach(() => localStorage.setItem("access", "a"));

  it("renders notifications with type badges", async () => {
    renderList();
    expect(await screen.findByText("You got a task")).toBeInTheDocument();
    expect(screen.getByText("Late")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^mark read$/i })).toBeInTheDocument();
  });

  it("marks all read without error", async () => {
    const user = userEvent.setup();
    renderList();
    await screen.findByText("You got a task");
    await user.click(screen.getByRole("button", { name: /mark all read/i }));
    await waitFor(() => expect(screen.getByText("You got a task")).toBeInTheDocument());
  });

  it("clicking per-row mark read fires without error", async () => {
    const user = userEvent.setup();
    renderList();
    await screen.findByText("You got a task");
    await user.click(screen.getByRole("button", { name: /^mark read$/i }));
    await waitFor(() => expect(screen.getByText("You got a task")).toBeInTheDocument());
  });
});
