import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { ToastProvider } from "../../contexts/ToastContext";
import Register from "./Register";

function renderRegister() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <ToastProvider>
        <MemoryRouter>
          <Register />
        </MemoryRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

describe("Register form", () => {
  beforeEach(() => localStorage.clear());

  it("rejects short password", async () => {
    const user = userEvent.setup();
    renderRegister();
    await user.type(screen.getByLabelText(/^username/i), "newuser");
    await user.type(screen.getByLabelText(/email/i), "new@pms.local");
    await user.type(screen.getByLabelText(/^password/i), "short");
    await user.click(screen.getByRole("button", { name: /create account/i }));
    expect(await screen.findByText(/password must be at least 8/i)).toBeInTheDocument();
  });

  it("rejects invalid email", async () => {
    const user = userEvent.setup();
    renderRegister();
    await user.type(screen.getByLabelText(/^username/i), "newuser");
    await user.type(screen.getByLabelText(/email/i), "not-an-email");
    await user.type(screen.getByLabelText(/^password/i), "validpass1");
    await user.click(screen.getByRole("button", { name: /create account/i }));
    expect(await screen.findByText(/email/i)).toBeInTheDocument();
  });

  it("shows error toast on duplicate username", async () => {
    const user = userEvent.setup();
    renderRegister();
    await user.type(screen.getByLabelText(/^username/i), "taken");
    await user.type(screen.getByLabelText(/email/i), "x@pms.local");
    await user.type(screen.getByLabelText(/^password/i), "validpass1");
    await user.click(screen.getByRole("button", { name: /create account/i }));
    await waitFor(() => {
      expect(screen.getByText(/already exists/i)).toBeInTheDocument();
    });
  });
});
