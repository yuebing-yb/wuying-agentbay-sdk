/**
 * Mobile Agent Streaming Example
 *
 * This example demonstrates:
 * 1. Mobile Agent task execution with real-time streaming output
 * 2. Using typed callbacks (onReasoning, onContent, onToolCall, onToolResult)
 * 3. Using unified onEvent callback for all event types
 */

import { AgentBay } from '../../../src/agent-bay';
import { AgentEvent, AgentStreamingOptions } from '../../../src/agent/agent';

async function exampleTypedCallbacks() {
  console.log('='.repeat(60));
  console.log('Example 1: Mobile Agent Streaming with Typed Callbacks');
  console.log('='.repeat(60));

  const client = new AgentBay();
  let session;

  try {
    const sessionResult = await client.create({
      imageId: 'imgc-0ab5takhnmlvhx9gp',
    });
    session = sessionResult.session!;
    console.log(`Session created: ${session.sessionId}`);

    const result = await session.agent.mobile.executeTaskAndWait(
      'Open Settings app',
      180,
      10,
      {
        onReasoning: (event: AgentEvent) => {
          process.stdout.write(`[Reasoning] ${event.content || ''}`);
        },
        onContent: (event: AgentEvent) => {
          process.stdout.write(`[Content] ${event.content || ''}`);
        },
        onToolCall: (event: AgentEvent) => {
          console.log(`\n[ToolCall] ${event.toolName}(${JSON.stringify(event.args)})`);
        },
        onToolResult: (event: AgentEvent) => {
          const preview = JSON.stringify(event.result).substring(0, 200);
          console.log(`[ToolResult] ${event.toolName} -> ${preview}`);
        },
      },
    );

    console.log(`\n\nTask completed:`);
    console.log(`  Success: ${result.success}`);
    console.log(`  Status: ${result.taskStatus}`);
    if (result.taskResult) {
      console.log(`  Result: ${result.taskResult.substring(0, 200)}`);
    }
  } finally {
    if (session) {
      await client.delete(session);
      console.log('Session cleaned up');
    }
  }
}

async function exampleUnifiedEventCallback() {
  console.log('\n' + '='.repeat(60));
  console.log('Example 2: Mobile Agent Streaming with Unified onEvent');
  console.log('='.repeat(60));

  const client = new AgentBay();
  let session;

  try {
    const sessionResult = await client.create({
      imageId: 'imgc-0ab5takhnmlvhx9gp',
    });
    session = sessionResult.session!;
    console.log(`Session created: ${session.sessionId}`);

    const events: AgentEvent[] = [];

    const result = await session.agent.mobile.executeTaskAndWait(
      'Open Settings app',
      180,
      10,
      {
        onEvent: (event: AgentEvent) => {
          events.push(event);
          if (event.type === 'reasoning') {
            process.stdout.write(`[R] ${event.content || ''}`);
          } else if (event.type === 'content') {
            process.stdout.write(`[C] ${event.content || ''}`);
          } else if (event.type === 'tool_call') {
            console.log(`\n[TC] ${event.toolName}(${JSON.stringify(event.args)})`);
          } else if (event.type === 'tool_result') {
            console.log(`[TR] ${event.toolName} -> ${JSON.stringify(event.result).substring(0, 100)}`);
          } else if (event.type === 'error') {
            console.log(`\n[ERR] ${event.content || JSON.stringify(event.error)}`);
          }
        },
      },
    );

    console.log(`\n\nTask completed:`);
    console.log(`  Success: ${result.success}`);
    console.log(`  Status: ${result.taskStatus}`);
    console.log(`  Total events: ${events.length}`);
    if (result.taskResult) {
      console.log(`  Result: ${result.taskResult.substring(0, 200)}`);
    }

    const breakdown: Record<string, number> = {};
    for (const e of events) {
      breakdown[e.type] = (breakdown[e.type] || 0) + 1;
    }
    console.log(`  Event breakdown: ${JSON.stringify(breakdown)}`);
  } finally {
    if (session) {
      await client.delete(session);
      console.log('Session cleaned up');
    }
  }
}

async function main() {
  console.log('Mobile Agent Streaming Output Examples\n');

  await exampleTypedCallbacks();
  await exampleUnifiedEventCallback();

  console.log('\nAll examples completed!');
}

main().catch(console.error);
