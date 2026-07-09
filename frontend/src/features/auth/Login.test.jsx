import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../../lib/queryClient";
import { AuthProvider } from "../../contexts/AuthContext";
import { ToastProvider } from "../../contexts/ToastContext";
import Login from "./Login";

function renderLogin() {
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AuthProvider>
          <MemoryRouter>
            <Login />
          </MemoryRouter>
        </AuthProvider>
      </ToastProvider>
    </QueryClientProvider>
  );
}

describe("Login form", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("shows validation error when fields are empty", async () => {
    const user = userEvent.setup();
    renderLogin();
    await user.click(screen.getByRole("button", { name: /log in/i }));
    expect(await screen.findByText(/username/i)).toBeInTheDocument();
  });

  it("shows error toast on wrong credentials", async () => {
    const user = userEvent.setup();
    renderLogin();
    await user.type(screen.getByLabelText(/username/i), "wrong");
    await user.type(screen.getByLabelText(/password/i), "wrongpass");
    await user.click(screen.getByRole("button", { name: /log in/i }));
    expect(await screen.findByText(/invalid username or password/i)).toBeInTheDocument();
  });

  it("logs in with valid credentials", async () => {
    const user = userEvent.setup();
    renderLogin();
    await user.type(screen.getByLabelText(/username/i), "member");
    await user.type(screen.getByLabelText(/password/i), "member12345");
    await user.click(screen.getByRole("button", { name: /log in/i }));
    // token stored after success
    await expect.poll(() => localStorage.getItem("access")).toBe("a");
  });
});
