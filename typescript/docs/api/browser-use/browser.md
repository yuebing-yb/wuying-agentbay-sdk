# Class: Browser

## 🌐 Related Tutorial

- [Browser Use Guide](../../../../docs/guides/browser-use/README.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,screenshot capture, and content extraction. It enables automated testing and web scraping workflows.


## Requirements

- Requires `browser_latest` image for browser automation features

## Hierarchy

- **`Browser`**

  ↳ ``LocalBrowser``

## Table of contents


### Properties


### Methods

- [destroy](#destroy)
- [initialize](#initialize)
- [initializeAsync](#initializeasync)
- [isInitialized](#isinitialized)
- [registerCallback](#registercallback)
- [screenshot](#screenshot)
- [sendNotifyMessage](#sendnotifymessage)
- [sendTakeoverDone](#sendtakeoverdone)
- [unregisterCallback](#unregistercallback)

## Properties

```typescript
operator: [`BrowserOperator`](browser-operator.md)
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
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'browser_latest' });
if (result.success) {
  const success = await result.session.browser.initializeAsync(new BrowserOptionClass());
  console.log('Browser initialized:', success);
  await result.session.delete();
}
```

___

### isInitialized

▸ **isInitialized**(): `boolean`

Returns true if the browser was initialized, false otherwise.

#### Returns

`boolean`

___

### registerCallback

▸ **registerCallback**(`callback`): `Promise`\<`boolean`\>

Register a callback function to handle browser-related push notifications from sandbox.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `callback` | ``BrowserCallback`` | Callback function that receives a BrowserNotifyMessage object containing notification details such as type, code, message, action, and extra_params. |

#### Returns

`Promise`\<`boolean`\>

Promise<boolean> - True if the callback was successfully registered.

**`Example`**

```typescript
function onBrowserCallback(notifyMsg: BrowserNotifyMessage) {
  console.log(`Type: ${notifyMsg.type}`);
  console.log(`Code: ${notifyMsg.code}`);
  console.log(`Message: ${notifyMsg.message}`);
  console.log(`Action: ${notifyMsg.action}`);
  console.log(`Extra params: ${JSON.stringify(notifyMsg.extraParams)}`);
}

const createResult = await agentBay.create();
const session = createResult.session;

// Initialize browser
await session.browser.initialize();

// Register callback
const success = await session.browser.registerCallback(onBrowserCallback);

// ... do work ...

// Unregister when done
await session.browser.unregisterCallback();
await session.delete();
```

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
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'browser_latest' });
if (result.success) {
  await result.session.browser.initializeAsync(new BrowserOptionClass());
  const browser = await chromium.connectOverCDP(await result.session.browser.getEndpointUrl());
  const page = await browser.contexts()[0].newPage();
  await page.goto('https://example.com');
  const screenshot = await result.session.browser.screenshot(page);
  await writeFile('screenshot.png', Buffer.from(screenshot));
  await browser.close();
  await result.session.delete();
}
```

___

### sendNotifyMessage

▸ **sendNotifyMessage**(`notifyMessage`): `Promise`\<`boolean`\>

Send a BrowserNotifyMessage to sandbox.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `notifyMessage` | ``BrowserNotifyMessage`` | The notify message to send. |

#### Returns

`Promise`\<`boolean`\>

Promise<boolean> - True if the notify message was successfully sent, False otherwise.

**`Example`**

```typescript
function onBrowserCallback(notifyMsg: BrowserNotifyMessage) {
  console.log(`Type: ${notifyMsg.type}`);
  console.log(`Code: ${notifyMsg.code}`);
  console.log(`Message: ${notifyMsg.message}`);
  console.log(`Action: ${notifyMsg.action}`);
  console.log(`Extra params: ${JSON.stringify(notifyMsg.extraParams)}`);
}

const createResult = await agentBay.create();
const session = createResult.session;

// Initialize browser
await session.browser.initialize();

// Register callback
const success = await session.browser.registerCallback(onBrowserCallback);

// ... do work ...

// Send notify message
const notifyMessage = new BrowserNotifyMessage(
  'call-for-user',
  3,
  199,
  'user handle done',
  'takeoverdone',
  {}
);
await session.browser.sendNotifyMessage(notifyMessage);

// Unregister when done
await session.browser.unregisterCallback();
await session.delete();
```

___

### sendTakeoverDone

▸ **sendTakeoverDone**(`notifyId`): `Promise`\<`boolean`\>

Send a takeoverdone notify message to sandbox.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `notifyId` | `number` | The notification ID associated with the takeover request message. |

#### Returns

`Promise`\<`boolean`\>

Promise<boolean> - True if the takeoverdone notify message was successfully sent, False otherwise.

**`Example`**

```typescript
function onBrowserCallback(notifyMsg: BrowserNotifyMessage) {
  // receive call-for-user "takeover" action
  if (notifyMsg.action === 'takeover') {
    const takeoverNotifyId = notifyMsg.id;

    // ... do work in other thread...
    // send takeoverdone notify message
    await session.browser.sendTakeoverDone(takeoverNotifyId);
    // ... end...
  }
}

const createResult = await agentBay.create();
const session = createResult.session;

// Initialize browser
await session.browser.initialize();

// Register callback
const success = await session.browser.registerCallback(onBrowserCallback);

// ... do work ...

// Unregister when done
await session.browser.unregisterCallback();
await session.delete();
```

___

### unregisterCallback

▸ **unregisterCallback**(): `Promise`\<`void`\>

Unregister the previously registered callback function.

#### Returns

`Promise`\<`void`\>

**`Example`**

```typescript
function onBrowserCallback(notifyMsg: BrowserNotifyMessage) {
  console.log(`Notification - Type: ${notifyMsg.type}, Message: ${notifyMsg.message}`);
}

const createResult = await agentBay.create();
const session = createResult.session;

await session.browser.initialize();

await session.browser.registerCallback(onBrowserCallback);

// ... do work ...

// Unregister callback
await session.browser.unregisterCallback();

await session.delete();
```

## Best Practices

1. Wait for page load completion before interacting with elements
2. Use appropriate selectors (CSS, XPath) for reliable element identification
3. Handle navigation timeouts and errors gracefully
4. Take screenshots for debugging and verification
5. Clean up browser resources after automation tasks


## Related Resources

- [Session API Reference](../common-features/basics/session.md)

