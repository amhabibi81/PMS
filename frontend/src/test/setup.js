import "@testing-library/jest-dom/vitest";
import { afterAll, beforeAll } from "vitest";
import { server } from "./msw";
import i18n, { setLanguage } from "../i18n";

beforeAll(() => {
  setLanguage("en");
  server.listen({ onUnhandledRequest: "error" });
});
afterAll(() => {
  server.close();
  i18n.changeLanguage("fa");
});
