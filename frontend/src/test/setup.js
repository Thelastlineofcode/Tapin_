import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock fetch for testing (jsdom provides fetch in test environment)
globalThis.fetch = vi.fn();

// Reset mocks after each test
afterEach(() => {
  vi.resetAllMocks();
});
