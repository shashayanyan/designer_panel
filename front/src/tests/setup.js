import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock XMLSerializer
global.XMLSerializer = class {
  serializeToString(node) {
    return node.outerHTML || ''
  }
}

// Mock URL methods
global.URL.createObjectURL = vi.fn(() => 'mock-url')
global.URL.revokeObjectURL = vi.fn()

// Mock canvas methods
HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
  fillStyle: '',
  fillRect: vi.fn(),
  drawImage: vi.fn(),
}))
HTMLCanvasElement.prototype.toDataURL = vi.fn(() => 'data:image/png;base64,mock')

// Mock Image.onload to trigger automatically (needed for renderSvgToPng hang)
global.Image = class {
  constructor() {
    this.onload = null;
    this.onerror = null;
    this.src = '';
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
}

// Mock HTMLAnchorElement.prototype.click to prevent "Not implemented: navigation" errors in JSDOM
// when triggering file downloads via a.click()
const originalClick = HTMLAnchorElement.prototype.click;
HTMLAnchorElement.prototype.click = function() {
  if (this.hasAttribute('download')) {
    // Just a placeholder, as JSDOM doesn't support downloads
    return;
  }
  originalClick.apply(this, arguments);
};
