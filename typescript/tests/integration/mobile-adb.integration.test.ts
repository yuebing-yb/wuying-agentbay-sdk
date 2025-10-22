/**
 * Integration tests for Mobile.getAdbUrl functionality.
 * Tests the complete E2E flow with real API.
 * 
 * Note: These tests create real sessions and should not be run concurrently
 * to avoid rate limiting and resource exhaustion.
 */

import { AgentBay } from '../../src/agent-bay';
import { log } from "../../src/utils/logger";

describe('Mobile GetAdbUrl Integration Tests', () => {
  let agentBay: AgentBay;
  const apiKey = process.env.AGENTBAY_API_KEY;

  beforeAll(() => {
    if (!apiKey) {
      console.warn('Warning: AGENTBAY_API_KEY not set. Tests will be skipped.');
    }
  });

  beforeEach(() => {
    if (apiKey) {
      agentBay = new AgentBay({ apiKey });
    }
  });

  describe('getAdbUrl with mobile_latest session', () => {
    test('should retrieve ADB URL and validate response structure', async () => {
      if (!apiKey) {
        log('Skipping test: AGENTBAY_API_KEY not set');
        return;
      }

      // Create mobile session
      const sessionResult = await agentBay.create({
        imageId: 'mobile_latest'
      });

      expect(sessionResult.session).toBeDefined();
      const session = sessionResult.session!;

      try {
        // Wait for session to be ready
        await new Promise(resolve => setTimeout(resolve, 15000));

        // Get ADB URL (adbkey_pub is not validated by server, using test value)
        const adbkeyPub = 'test_adb_key_123';
        const result = await session.mobile.getAdbUrl(adbkeyPub);

        // Verify result structure
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();
        expect(result.data).toContain('adb connect');
        expect(result.requestId).toBeDefined();
        expect(result.requestId.length).toBeGreaterThan(0);

        log(`✅ ADB URL: ${result.data}`);
        log(`✅ Request ID: ${result.requestId}`);

        // Verify URL format: "adb connect <IP>:<Port>"
        const parts = result.data!.split(' ');
        expect(parts.length).toBe(3);
        expect(parts[0]).toBe('adb');
        expect(parts[1]).toBe('connect');

        // Verify IP:Port format
        const addressParts = parts[2].split(':');
        expect(addressParts.length).toBe(2);

        log(`✅ Parsed ADB URL - IP: ${addressParts[0]}, Port: ${addressParts[1]}`);
      } finally {
        // Cleanup
        await session.delete();
      }
    }, 60000); // 60 second timeout
  });

  describe('getAdbUrl with non-mobile session', () => {
    test('should fail on browser_latest image', async () => {
      if (!apiKey) {
        log('Skipping test: AGENTBAY_API_KEY not set');
        return;
      }

      const sessionResult = await agentBay.create({
        imageId: 'browser_latest'
      });

      expect(sessionResult.session).toBeDefined();
      const session = sessionResult.session!;

      try {
        await new Promise(resolve => setTimeout(resolve, 10000));

        const adbkeyPub = 'test_key_456';
        const result = await session.mobile.getAdbUrl(adbkeyPub);

        // Should fail because this is not a mobile environment
        expect(result.success).toBe(false);
        expect(result.errorMessage).toBeDefined();
        expect(result.errorMessage.toLowerCase()).toContain('mobile');

        log(`✅ Expected error: ${result.errorMessage}`);
      } finally {
        await session.delete();
      }
    }, 60000);
  });
});
