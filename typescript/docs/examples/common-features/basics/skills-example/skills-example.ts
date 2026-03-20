import { AgentBay, CreateSessionParams, log, logError } from 'wuying-agentbay-sdk';

async function main() {
  const apiKey = process.env.AGENTBAY_API_KEY || 'akm-xxx';
  if (!process.env.AGENTBAY_API_KEY) {
    log('Warning: Set AGENTBAY_API_KEY environment variable.');
    return;
  }

  const agentBay = new AgentBay({ apiKey });

  try {
    // 1. Get skills metadata (no sandbox needed)
    log('Getting skills metadata...');
    const metadata = await agentBay.betaSkills.getMetadata();
    log(`Skills root path: ${metadata.skillsRootPath}`);
    log(`Available skills: ${metadata.skills.length}`);
    for (const skill of metadata.skills) {
      log(`  - ${skill.name}: ${skill.description}`);
    }

    // 2. Get metadata filtered by group IDs
    log('\nGetting skills metadata filtered by group...');
    const filtered = await agentBay.betaSkills.getMetadata({
      skillNames: ['5kvAvffm'],
    });
    log(`Filtered skills: ${filtered.skills.length}`);

    // 3. Create session with skills loaded
    log('\nCreating session with skills...');
    const params = new CreateSessionParams({
      loadSkills: true,
    });
    const result = await agentBay.create(params);
    if (!result.success || !result.session) {
      logError(`Session creation failed: ${result.errorMessage}`);
      return;
    }

    const session = result.session;
    log(`Session created: ${session.sessionId}`);

    // 4. Get metadata via betaSkills.getMetadata() for skills path and verification
    const sessionMetadata = await agentBay.betaSkills.getMetadata({
      imageId: params.imageId,
      skillNames: params.skillNames,
    });
    log(`Skills root path: ${sessionMetadata.skillsRootPath}`);
    log(`Skills count: ${sessionMetadata.skills.length}`);

    // 5. Verify skills in sandbox
    if (sessionMetadata.skillsRootPath) {
      const lsResult = await session.command.executeCommand(
        `ls ${sessionMetadata.skillsRootPath}`
      );
      log(`\nSkills directory contents:\n${lsResult.output}`);
    }

    // Cleanup
    await agentBay.delete(session);
    log('\nSession deleted.');
  } catch (error) {
    logError('Error:', error);
  }
}

main();
