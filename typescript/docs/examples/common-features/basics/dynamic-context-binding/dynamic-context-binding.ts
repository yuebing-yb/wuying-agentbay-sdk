#!/usr/bin/env node

/**
 * AgentBay SDK - Dynamic Context Binding Example
 *
 * This example demonstrates how to dynamically bind contexts to a running session:
 * - Create a session without any initial context
 * - Dynamically bind a context using session.context.bind()
 * - List current bindings using session.context.listBindings()
 * - Verify the bound context is usable
 */

import { AgentBay, ContextSync, logError, newSyncPolicy } from 'wuying-agentbay-sdk';

async function main(): Promise<void> {
    console.log('🔗 AgentBay Dynamic Context Binding Example');

    const apiKey = process.env.AGENTBAY_API_KEY || '';
    if (!apiKey) {
        console.log('❌ Please set AGENTBAY_API_KEY environment variable');
        process.exit(1);
    }

    const agentBay = new AgentBay({ apiKey });

    try {
        await dynamicBindingDemo(agentBay);
    } catch (error) {
        console.log(`❌ Example execution failed: ${error}`);
        logError('Error:', error);
    }

    console.log('✅ Dynamic context binding example completed');
}

async function dynamicBindingDemo(agentBay: AgentBay): Promise<void> {
    console.log('\n🔄 === Dynamic Context Binding Demonstration ===');

    // Step 1: Create a context
    console.log('\n📦 Step 1: Creating a context...');
    const contextResult = await agentBay.context.get('dynamic-bind-demo', true);
    if (!contextResult.success) {
        console.log(`❌ Context creation failed: ${contextResult.errorMessage}`);
        return;
    }

    const context = contextResult.context!;
    console.log(`✅ Context ready: ${context.id} (${context.name})`);

    // Step 2: Create a session WITHOUT any initial context
    console.log('\n🔧 Step 2: Creating a session (no initial context)...');
    const sessionResult = await agentBay.create();
    if (!sessionResult.success) {
        console.log(`❌ Session creation failed: ${sessionResult.errorMessage}`);
        return;
    }

    const session = sessionResult.session!;
    console.log(`✅ Session created: ${session.sessionId}`);

    try {
        // Step 3: List bindings - should be empty
        console.log('\n📋 Step 3: Listing bindings (should be empty)...');
        let bindingsResult = await session.context.listBindings();
        if (bindingsResult.success) {
            console.log(`   Current bindings: ${bindingsResult.bindings.length}`);
        }

        // Step 4: Dynamically bind the context
        console.log('\n🔗 Step 4: Dynamically binding context to session...');
        const syncPolicy = newSyncPolicy();
        const contextSync = new ContextSync(context.id, '/tmp/ctx-dynamic', syncPolicy);

        const bindResult = await session.context.bind(contextSync);
        if (bindResult.success) {
            console.log(`✅ Context bound successfully (RequestId: ${bindResult.requestId})`);
        } else {
            console.log(`❌ Bind failed: ${bindResult.errorMessage}`);
            return;
        }

        // Step 5: List bindings again - should show the bound context
        console.log('\n📋 Step 5: Listing bindings (should show 1 binding)...');
        bindingsResult = await session.context.listBindings();
        if (bindingsResult.success) {
            console.log(`   Current bindings: ${bindingsResult.bindings.length}`);
            for (const b of bindingsResult.bindings) {
                console.log(`   - Context: ${b.contextId}, Path: ${b.path}, Name: ${b.contextName}`);
            }
        }

        // Step 6: Verify the bound context is usable
        console.log('\n✍️ Step 6: Writing data to the bound context path...');
        const cmdResult = await session.command.executeCommand(
            "echo 'Hello from dynamic binding!' > /tmp/ctx-dynamic/test.txt"
        );
        if (cmdResult.exitCode === 0) {
            console.log('✅ Data written successfully');
        }

        const readResult = await session.fileSystem.readFile('/tmp/ctx-dynamic/test.txt');
        if (readResult.success) {
            console.log(`✅ Data read back: ${readResult.content.trim()}`);
        } else {
            console.log(`❌ Failed to read data: ${readResult.errorMessage}`);
        }

        // Step 7: Bind multiple contexts at once
        console.log('\n🔗 Step 7: Demonstrating multiple context binding...');
        const ctxResA = await agentBay.context.get('dynamic-bind-demo-a', true);
        const ctxResB = await agentBay.context.get('dynamic-bind-demo-b', true);
        if (ctxResA.success && ctxResB.success) {
            const csA = new ContextSync(ctxResA.context!.id, '/tmp/ctx-multi-a', syncPolicy);
            const csB = new ContextSync(ctxResB.context!.id, '/tmp/ctx-multi-b', syncPolicy);
            const bindResult2 = await session.context.bind([csA, csB]);
            if (bindResult2.success) {
                console.log('✅ Multiple contexts bound successfully');
            }

            bindingsResult = await session.context.listBindings();
            if (bindingsResult.success) {
                console.log(`   Total bindings: ${bindingsResult.bindings.length}`);
                for (const b of bindingsResult.bindings) {
                    console.log(`   - ${b.contextName} -> ${b.path}`);
                }
            }
        }

    } finally {
        console.log('\n🧹 Cleaning up...');
        await agentBay.delete(session, true);
        console.log('✅ Session deleted');
    }
}

if (require.main === module) {
    main().catch(error => {
        logError('Error in main execution:', error);
        process.exit(1);
    });
}
