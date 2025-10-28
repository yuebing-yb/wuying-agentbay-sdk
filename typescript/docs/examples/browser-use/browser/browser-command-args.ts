/**
 * Example demonstrating Browser Launch with Custom Command Arguments and 
 * go to Default Navigation URL with AgentBay SDK.
 *
 * This example shows how to configure browser with custom command arguments
 * and go to default navigation URL:
 * - Create AIBrowser session with custom command arguments and go to default navigation URL
 * - Use playwright to connect to AIBrowser instance through CDP protocol
 * - Verify the browser navigated to the default URL
 * - Test custom command arguments effects
 */

// @ts-nocheck
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';
import { BrowserOption } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';

async function main(): Promise<void> {
    // Get API key from environment variable
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
        console.log('Error: AGENTBAY_API_KEY environment variable not set');
        return;
    }

    try {
        // Initialize AgentBay client
        console.log('Initializing AgentBay client...');
        const agentBay = new AgentBay({ apiKey });

        // Create a session
        console.log('Creating a new session...');
        const params: CreateSessionParams = {
            imageId: 'linux_latest',
        };
        const sessionResult = await agentBay.create(params);

        if (!sessionResult.success) {
            console.log('Failed to create session');
            return;
        }

        const session = sessionResult.session;
        console.log(`Session created with ID: ${session.sessionId}`);

        // Create browser option with user defined cmd args and default navigate url
        const browserOption: BrowserOption = {
            cmdArgs: ['--disable-features=PrivacySandboxSettings4'],
            defaultNavigateUrl: 'chrome://version/',
        };

        console.log('Browser configuration:');
        console.log('- Command arguments:', browserOption.cmdArgs);
        console.log('- Default navigate URL:', browserOption.defaultNavigateUrl);

        const initialized = await session.browser.initializeAsync(browserOption);
        if (initialized) {
            const endpointUrl = await session.browser.getEndpointUrl();
            console.log('endpoint_url =', endpointUrl);

            const browser = await chromium.connectOverCDP(endpointUrl);
            const context = browser.contexts()[0];
            console.log('page count =', context.pages().length);
            const page = context.pages()[0];

            try {
                // Check if browser navigated to default URL
                console.log('\n--- Check Default Navigation ---');
                await page.waitForTimeout(2000); // Wait for navigation
                const currentUrl = page.url();
                console.log('Current URL:', currentUrl);
                
                if (currentUrl.includes('chrome://version/')) {
                    console.log('✓ Browser successfully navigated to default URL');
                } else {
                    console.log('✗ Browser did not navigate to default URL');
                }

                // Test command arguments effect by checking Chrome version page
                if (currentUrl.includes('chrome://version/')) {
                    console.log('\n--- Check Chrome Version Info ---');
                    const versionInfo = await page.evaluate(() => {
                        const versionElement = document.querySelector('#version');
                        const commandLineElement = document.querySelector('#command_line');
                        return {
                            version: versionElement ? versionElement.textContent : 'Not found',
                            commandLine: commandLineElement ? commandLineElement.textContent : 'Not found'
                        };
                    });
                    
                    console.log('Chrome Version:', versionInfo.version);
                    console.log('Command Line:', versionInfo.commandLine);
                    
                    if (versionInfo.commandLine.includes('--disable-features=PrivacySandboxSettings4')) {
                        console.log('✓ Custom command argument found in browser');
                    } else {
                        console.log('✗ Custom command argument not found in browser');
                    }
                }

                await page.waitForTimeout(3000);
            } finally {
                await browser.close();
            }
            await session.browser.destroy();
        }

        // Clean up session
        await agentBay.delete(session);
    } catch (error) {
        console.error('Error:', error);
    }
}

if (require.main === module) {
    main().catch(console.error);
}
