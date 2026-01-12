/**
 * Mobile GetAllUIElements (XML) Example
 *
 * This example demonstrates how to retrieve raw XML UI hierarchy via
 * Mobile.getAllUIElements(format="xml").
 */

import { AgentBay } from 'wuying-agentbay-sdk';

async function main() {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    console.error('Error: AGENTBAY_API_KEY environment variable is not set');
    process.exit(1);
  }

  const client = new AgentBay({ apiKey });

  const sessionResult = await client.create({
    imageId: 'imgc-0ab5takhnlaixj11v'
  });

  if (!sessionResult.session) {
    console.error('Failed to create session');
    process.exit(1);
  }

  const session = sessionResult.session;
  try {
    await new Promise(resolve => setTimeout(resolve, 15000));

    const ui = await session.mobile.getAllUIElements(10000, 'xml');
    if (!ui.success) {
      console.error(`getAllUIElements(xml) failed: ${ui.errorMessage}`);
      process.exit(1);
    }

    console.log(`RequestID: ${ui.requestId}`);
    console.log(`Format: ${ui.format}`);
    console.log(`Raw length: ${ui.raw.length}`);
    console.log(`Elements: ${ui.elements.length}`);
  } finally {
    await session.delete();
  }
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});

