/**
 * Test setup file to configure the test environment
 * This file is executed before running tests
 */

import { setupLogger } from '../src/utils/logger';

// Check if we should suppress logs (can be controlled via environment variable)
// Default to true for unit tests to reduce noise
const suppressLogs = process.env.SUPPRESS_TEST_LOGS !== 'false';

if (suppressLogs) {
  // Disable console logging during tests to avoid noise in test output
  // This prevents expected error messages from appearing as test failures in CI/CD
  setupLogger({
    enableConsole: false,
    level: 'ERROR' // Only log critical errors
  });
}
