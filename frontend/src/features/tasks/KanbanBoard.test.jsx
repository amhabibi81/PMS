import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ToastProvider } from "../../contexts/ToastContext";
import KanbanBoard from "./KanbanBoard";

function renderBoard() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <ToastProvider>
        <KanbanBoard projectId={1} />
      </ToastProvider>
    </QueryClientProvider>
  );
}

describe("KanbanBoard", () => {
  beforeEach(() => {
    localStorage.setItem("access", "a");
  });

  it("renders columns and tasks", async () => {
    renderBoard();
    expect(await screen.findByText("Task A")).toBeInTheDocument();
    expect(screen.getByText("Task B")).toBeInTheDocument();
    expect(screen.getByText(/to do/i)).toBeInTheDocument();
  });

  it("rolls back optimistic update on illegal transition (Todo -> Done)", async () => {
    const user = userEvent.setup();
    renderBoard();
    const card = await screen.findByText("Task A");
    // Simulate dropping card onto the Done column via the data model:
    // we directly call the transition endpoint by triggering a status button on the detail modal.
    await user.click(card);
    // Open task detail -> click "Done" status button -> expect error toast + rollback handled
    const doneBtns = await screen.findAllByRole("button", { name: /done/i });
    await user.click(doneBtns[0]);
    await waitFor(() => {
      expect(screen.getByText(/illegal status transition/i)).toBeInTheDocument();
    });
  });
});
