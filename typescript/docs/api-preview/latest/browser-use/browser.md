# Class: Browser

## 🌐 Related Tutorial

- [Browser Use Guide](../../../../../docs/guides/browser-use/README.md) - Complete guide to browser automation

## Table of contents

### Constructors

- [constructor](browser.md#constructor)

### Properties

- [agent](browser.md#agent)

### Methods

- [destroy](browser.md#destroy)
- [getEndpointUrl](browser.md#getendpointurl)
- [getOption](browser.md#getoption)
- [initialize](browser.md#initialize)
- [initializeAsync](browser.md#initializeasync)
- [isInitialized](browser.md#isinitialized)
- [screenshot](browser.md#screenshot)

## Constructors

### constructor

• **new Browser**(`session`): [`Browser`](browser.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `session` | [`Session`](../common-features/basics/session.md) |

#### Returns

[`Browser`](browser.md)

## Properties

### agent

• **agent**: ``BrowserAgent``

## Methods

### destroy

▸ **destroy**(): `Promise`\<`void`\>

Destroy the browser instance.

#### Returns

`Promise`\<`void`\>

___

### getEndpointUrl

▸ **getEndpointUrl**(): `Promise`\<`string`\>

Returns the endpoint URL if the browser is initialized, otherwise throws an exception.
When initialized, always fetches the latest CDP url from session.getLink().

#### Returns

`Promise`\<`string`\>

___

### getOption

▸ **getOption**(): ``null`` \| ``BrowserOptionClass``

Returns the current BrowserOption used to initialize the browser, or null if not set.

#### Returns

``null`` \| ``BrowserOptionClass``

___

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

| Name | Type |
| :------ | :------ |
| `option` | ``BrowserOption`` \| ``BrowserOptionClass`` |

#### Returns

`Promise`\<`boolean`\>

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
| :------ | :------ | :------ | :---## Related Resources

- [Extension API Reference](../../browser-use/extension.md)
- [Session API Reference](../../browser-use/session.md)


--- |
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
