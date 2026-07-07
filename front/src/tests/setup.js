import "@testing-library/jest-dom";
import { vi } from "vitest";

// Mock XMLSerializer
global.XMLSerializer = class {
  serializeToString(node) {
    return node.outerHTML || "";
  }
};

// Mock URL methods
global.URL.createObjectURL = vi.fn(() => "mock-url");
global.URL.revokeObjectURL = vi.fn();

// Mock canvas methods
HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
  fillStyle: "",
  fillRect: vi.fn(),
  drawImage: vi.fn(),
}));
HTMLCanvasElement.prototype.toDataURL = vi.fn(
  () => "data:image/png;base64,mock",
);

// Mock Image.onload to trigger automatically (needed for renderSvgToPng hang)
global.Image = class {
  constructor() {
    this.onload = null;
    this.onerror = null;
    this.src = "";
  }
  set src(value) {
    this._src = value;
    // Trigger onload asynchronously to simulate image load
    setTimeout(() => {
      if (this.onload) this.onload();
    }, 0);
  }
  get src() {
    return this._src;
  }
};

// Mock HTMLAnchorElement.prototype.click to prevent "Not implemented: navigation" errors in JSDOM
// when triggering file downloads via a.click()
const originalClick = HTMLAnchorElement.prototype.click;
HTMLAnchorElement.prototype.click = function () {
  if (this.hasAttribute("download")) {
    // Just a placeholder, as JSDOM doesn't support downloads
    return;
  }
  originalClick.apply(this, arguments);
};

// Global fetch mock with robust default
global.fetch = vi.fn((url) => {
  if (url && typeof url === "string" && url.includes("/motor-start-text/")) {
    return Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve({
          description: "Mock desc",
          technical_characteristics: "Mock tech",
          functions: "Mock functions",
          protections: "Mock protections",
        }),
    });
  }
  return Promise.resolve({
    ok: true,
    json: () => Promise.resolve([]),
    blob: () => Promise.resolve(new Blob([""])),
  });
});

// Configure VITE_SUPABASE_URL to prevent placeholder bypass during tests
import.meta.env.VITE_SUPABASE_URL = "https://mock-supabase-project.supabase.co";
import.meta.env.VITE_SUPABASE_ANON_KEY = "mock-anon-key";

// Mock Supabase to return verified session and allowed app permissions in tests
vi.mock("../supabase", () => {
  return {
    supabase: {
      auth: {
        getSession: vi.fn(() =>
          Promise.resolve({
            data: {
              session: {
                user: { id: "test-user-id" },
              },
            },
            error: null,
          })
        ),
      },
      from: vi.fn(() => ({
        select: vi.fn(() => ({
          eq: vi.fn(() => ({
            single: vi.fn(() =>
              Promise.resolve({
                data: { allowed_apps: ["designer"] },
                error: null,
              })
            ),
          })),
        })),
      })),
    },
  };
});


