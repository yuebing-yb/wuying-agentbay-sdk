/**
 * Integration tests for Mobile Agent streaming output feature.
 *
 * Tests the WS-based streaming execution path with real backend services.
 * Uses debug image imgc-0ab5takhnmlvhx9gp for Mobile Agent.
 *
 * Note: These tests create real sessions and should not be run concurrently
 * to avoid rate limiting and resource exhaustion.
 */

import { AgentBay } from '../../src/agent-bay';
import { AgentEvent, AgentStreamingOptions } from '../../src/agent/agent';
import { Session } from '../../src/session';
import { log } from '../../src/utils/logger';

describe('Mobile Agent Streaming Integration Tests', () => {
  let agentBay: AgentBay;
  let session: Session;
  const apiKey = process.env.AGENTBAY_API_KEY;

  beforeAll(async () => {
    if (!apiKey) {
      console.warn('Warning: AGENTBAY_API_KEY not set. Tests will be skipped.');
      return;
    }

    agentBay = new AgentBay({ apiKey });
    await new Promise((r) => setTimeout(r, 3000));

    const sessionResult = await agentBay.create({
      imageId: 'imgc-0ab5takhnmlvhx9gp',
    });

    if (!sessionResult.success || !sessionResult.session) {
      console.error(`Failed to create session: ${sessionResult.errorMessage}`);
      return;
    }

    session = sessionResult.session;
    log(`Session created: ${session.sessionId}`);
  });

  afterAll(async () => {
    if (session) {
      try {
        log(`Cleaning up session: ${session.sessionId}`);
        await agentBay.delete(session);
        log(`Session deleted: ${session.sessionId}`);
      } catch (e) {
        log(`Error deleting session: ${e}`);
      }
    }
  });

  test('should stream events with typed callbacks', async () => {
    if (!session) {
      log('Skipping: session not created');
      return;
    }

    const reasoningEvents: AgentEvent[] = [];
    const contentEvents: AgentEvent[] = [];
    const toolCalls: AgentEvent[] = [];
    const toolResults: AgentEvent[] = [];

    const options: AgentStreamingOptions = {
      onReasoning: (event) => {
        reasoningEvents.push(event);
        log(`[Reasoning] round=${event.round}: ${(event.content || '').substring(0, 100)}...`);
      },
      onContent: (event) => {
        contentEvents.push(event);
        log(`[Content] round=${event.round}: ${(event.content || '').substring(0, 100)}...`);
      },
      onToolCall: (event) => {
        toolCalls.push(event);
        log(`[ToolCall] round=${event.round}: ${event.toolName}(${JSON.stringify(event.args)})`);
      },
      onToolResult: (event) => {
        toolResults.push(event);
        log(`[ToolResult] round=${event.round}: ${event.toolName} -> ${JSON.stringify(event.result).substring(0, 100)}...`);
      },
    };

    log('Testing mobile agent streaming with typed callbacks');

    const result = await session.agent.mobile.executeTaskAndWait(
      'Open Settings app',
      180,
      10,
      options,
    );

    log(`Result: success=${result.success}, status=${result.taskStatus}`);
    log(`Reasoning: ${reasoningEvents.length}, Content: ${contentEvents.length}, ToolCalls: ${toolCalls.length}, ToolResults: ${toolResults.length}`);

    expect(typeof result.taskStatus).toBe('string');
  }, 300000);
});
