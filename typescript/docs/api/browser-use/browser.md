# Class: Browser

## 🌐 Related Tutorial

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,
screenshot capture, and content extraction. It enables automated testing and web scraping workflows.


## Requirements

- Requires `browser_latest` image for browser automation features

## Table of contents


### Properties


### Methods

- [destroy](browser.md#destroy)
- [initialize](browser.md#initialize)
- [initializeAsync](browser.md#initializeasync)
- [isInitialized](browser.md#isinitialized)
- [screenshot](browser.md#screenshot)

## Properties

```typescript
agent: ``BrowserAgent``
```


## Methods

### destroy

▸ **destroy**(): `Promise`\<`void`\>

Destroy the browser instance.

#### Returns

`Promise`\<`void`\>

### initialize

▸ **initialize**(`option`): `boolean`

Initialize the browser instance with the given options.
Returns true if successful, false otherwise.

#### Parameters

| Name | Type |
| :------ | :------ |
| `option` | ``BrowserOption`` \| ``BrowserOptionClass`` |

#### Returns

`boolean`

___

### initializeAsync

▸ **initializeAsync**(`option`): `Promise`\<`boolean`\>

Initialize the browser instance with the given options asynchronously.
Returns true if successful, false otherwise.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `option` | ``BrowserOption`` \| ``BrowserOptionClass`` | Browser configuration options |

#### Returns

`Promise`\<`boolean`\>

Promise resolving to true if successful, false otherwise

**`Example`**

```typescript
import { AgentBay, BrowserOptionClass } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function initializeBrowser() {
    try {
        const result = await agentBay.create({ imageId: 'browser_latest' });
        if (result.success && result.session) {
            const session = result.session;

            // Initialize browser with basic options
            const option = new BrowserOptionClass();
            const success = await session.browser.initializeAsync(option);

            if (success) {
                console.log('Browser initialized successfully');

                // Use the browser...

                await session.delete();
            }
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

initializeBrowser().catch(console.error);
```

___

### isInitialized

▸ **isInitialized**(): `boolean`

Returns true if the browser was initialized, false otherwise.

#### Returns

`boolean`

___

### screenshot

▸ **screenshot**(`page`, `fullPage?`, `options?`): `Promise`\<`Uint8Array`\>

Takes a screenshot of the specified page with enhanced options and error handling.
This method requires the caller to connect to the browser via Playwright or similar
and pass the page object to this method.

Note: This is a placeholder method that indicates where screenshot functionality
should be implemented. In a complete implementation, this would use Playwright's
page.screenshot() method or similar browser automation API.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `page` | `any` | `undefined` | The Playwright Page object to take a screenshot of. This is a required parameter. |
| `fullPage` | `boolean` | `false` | Whether to capture the full scrollable page. Defaults to false. |
| `options` | `Record`\<`string`, `any`\> | `{}` | Additional screenshot options that will override defaults. Common options include: - type: Image type, either 'png' or 'jpeg' (default: 'png') - quality: Quality of the image, between 0-100 (jpeg only) - timeout: Maximum time in milliseconds (default: 60000) - animations: How to handle animations (default: 'disabled') - caret: How to handle the caret (default: 'hide') - scale: Scale setting (default: 'css') |

#### Returns

`Promise`\<`Uint8Array`\>

Screenshot data as Uint8Array.

**`Throws`**

BrowserError If browser is not initialized.

**`Throws`**

Error If screenshot capture fails.

**`Example`**

```typescript
import { AgentBay, BrowserOptionClass } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';
import { writeFile } from 'fs/promises';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateScreenshot() {
    try {
        const result = await agentBay.create({ imageId: 'browser_latest' });
        if (result.success && result.session) {
            const session = result.session;

            // Initialize browser
            const option = new BrowserOptionClass();
            await session.browser.initializeAsync(option);

            // Get CDP endpoint and connect with Playwright
            const endpointUrl = await session.browser.getEndpointUrl();
            const browser = await chromium.connectOverCDP(endpointUrl);
            const context = browser.contexts()[0];
            const page = await context.newPage();

            // Navigate to a page
            await page.goto('https://example.com');

            // Take a simple screenshot (viewport only)
            const screenshotData = await session.browser.screenshot(page);
            await writeFile('screenshot.png', Buffer.from(screenshotData));

            // Take a full page screenshot
            const fullPageData = await session.browser.screenshot(page, true);
            await writeFile('full_page.png', Buffer.from(fullPageData));

            // Take a screenshot with custom options
            const customScreenshot = await session.browser.screenshot(
                page,
                false,
                {
                    type: 'jpeg',
                    quality: 80,
                    timeout: 30000
                }
            );
            await writeFile('custom_screenshot.jpg', Buffer.from(customScreenshot));

            await browser.close();
            await session.delete();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

demonstrateScreenshot().catch(console.error);
```

## Best Practices

1. Wait for page load completion before interacting with elements
2. Use appropriate selectors (CSS, XPath) for reliable element identification
3. Handle navigation timeouts and errors gracefully
4. Take screenshots for debugging and verification
5. Clean up browser resources after automation tasks


## Related Resources

- [Session API Reference](../common-features/basics/session.md)

