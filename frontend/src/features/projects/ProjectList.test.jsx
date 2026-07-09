import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastProvider } from "../../contexts/ToastContext";
import ProjectList from "./ProjectList";

function renderList() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <ToastProvider>
        <MemoryRouter>
          <ProjectList />
        </MemoryRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

describe("ProjectList", () => {
  beforeEach(() => localStorage.setItem("access", "a"));

  it("lists projects from the API", async () => {
    renderList();
    expect(await screen.findByText("Demo")).toBeInTheDocument();
    expect(screen.getByText(/50%/)).toBeInTheDocument();
  });

  it("opens the create modal and submits a new project", async () => {
    const user = userEvent.setup();
    renderList();
    await screen.findByText("Demo");
    await user.click(screen.getByRole("button", { name: /new project/i }));
    expect(await screen.findByRole("heading", { name: /new project/i })).toBeInTheDocument();
    await user.type(screen.getByLabelText(/title/i), "My Project");
    await user.click(screen.getByRole("button", { name: /^create$/i }));
    // modal closes on success
    await waitFor(() => {
      expect(screen.queryByRole("heading", { name: /new project/i })).not.toBeInTheDocument();
    });
  });
});
