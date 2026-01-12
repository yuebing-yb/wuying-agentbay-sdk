/**
 * Integration tests for Mobile.getAllUIElements XML format.
 *
 * Note: This test creates a real session. Do not run concurrently.
 */

import { AgentBay } from '../../src/agent-bay';
import { log } from "../../src/utils/logger";

describe('Mobile GetAllUIElements XML Integration Tests', () => {
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

  test('should return XML raw output for get_all_ui_elements', async () => {
    if (!apiKey) {
      log('Skipping test: AGENTBAY_API_KEY not set');
      return;
    }

    const sessionResult = await agentBay.create({
      imageId: 'imgc-0ab5takhnlaixj11v'
    });

    expect(sessionResult.session).toBeDefined();
    const session = sessionResult.session!;

    try {
      await new Promise(resolve => setTimeout(resolve, 15000));

      const ui = await session.mobile.getAllUIElements(10000, 'xml');

      expect(ui.success).toBe(true);
      expect(ui.requestId).toBeDefined();
      expect(ui.requestId.length).toBeGreaterThan(0);
      expect(ui.format).toBe('xml');
      expect(typeof ui.raw).toBe('string');
      expect(ui.raw.trim()).not.toBe('');
      expect(ui.raw.trim().startsWith('<?xml')).toBe(true);
      expect(ui.raw).toContain('<hierarchy');
      expect(ui.elements).toEqual([]);
    } finally {
      await session.delete();
    }
  }, 60000);
});

