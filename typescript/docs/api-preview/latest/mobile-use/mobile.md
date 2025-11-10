# Class: Mobile

## 📱 Related Tutorial

- [Mobile Use Guide](../../../../../docs/guides/mobile-use/README.md) - Automate mobile applications

## Overview

The Mobile module provides mobile device automation capabilities including touch gestures,
text input, app management, and screenshot capture. It supports Android device automation.


## Requirements

- Requires `mobile_latest` image for mobile automation features

## Table of contents


### Methods

- [configure](mobile.md#configure)
- [inputText](mobile.md#inputtext)
- [screenshot](mobile.md#screenshot)
- [sendKey](mobile.md#sendkey)
- [setAppBlacklist](mobile.md#setappblacklist)
- [setAppWhitelist](mobile.md#setappwhitelist)
- [setNavigationBarVisibility](mobile.md#setnavigationbarvisibility)
- [setResolutionLock](mobile.md#setresolutionlock)
- [setUninstallBlacklist](mobile.md#setuninstallblacklist)
- [startApp](mobile.md#startapp)
- [stopAppByCmd](mobile.md#stopappbycmd)
- [swipe](mobile.md#swipe)
- [tap](mobile.md#tap)

## Methods

### configure

▸ **configure**(`config`): `Promise`\<`OperationResult`\>

Configure mobile device settings based on MobileExtraConfig.
This method applies various mobile configuration settings including
resolution lock and app access management.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `config` | ``MobileExtraConfig`` | The mobile configuration to apply |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure

### inputText

▸ **inputText**(`text`): `Promise`\<`BoolResult`\>

Input text at the current focus position.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `text` | `string` | Text to input |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to BoolResult with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateInputText() {
  try {
    const result = await agentBay.create({ imageId: 'mobile_latest' });
    if (result.success && result.session) {
      const session = result.session;

      // Input text at current focus position
      const inputResult = await session.mobile.inputText('Hello Mobile');
      if (inputResult.success) {
        console.log('Text input successfully');
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateInputText().catch(console.error);
```

___

### screenshot

▸ **screenshot**(): `Promise`\<`ScreenshotResult`\>

Take a screenshot of the current mobile screen.

#### Returns

`Promise`\<`ScreenshotResult`\>

Promise resolving to ScreenshotResult containing screenshot URL

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateScreenshot() {
  try {
    const result = await agentBay.create({ imageId: 'mobile_latest' });
    if (result.success && result.session) {
      const session = result.session;

      // Take a screenshot
      const screenshotResult = await session.mobile.screenshot();
      if (screenshotResult.success) {
        console.log('Screenshot taken successfully');
        console.log(`Screenshot URL: ${screenshotResult.data}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateScreenshot().catch(console.error);
```

___

### sendKey

▸ **sendKey**(`key`): `Promise`\<`BoolResult`\>

Send Android key code.

#### Parameters

| Name | Type |
| :------ | :------ |
| `key` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

___

### setAppBlacklist

▸ **setAppBlacklist**(`packageNames`): `Promise`\<`OperationResult`\>

Set app blacklist configuration.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `packageNames` | `string`[] | List of package names to blacklist |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure

___

### setAppWhitelist

▸ **setAppWhitelist**(`packageNames`): `Promise`\<`OperationResult`\>

Set app whitelist configuration.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `packageNames` | `string`[] | List of package names to whitelist |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure

___

### setNavigationBarVisibility

▸ **setNavigationBarVisibility**(`hide`): `Promise`\<`OperationResult`\>

Set navigation bar visibility for mobile devices.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `hide` | `boolean` | True to hide navigation bar, false to show navigation bar |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure

___

### setResolutionLock

▸ **setResolutionLock**(`enable`): `Promise`\<`OperationResult`\>

Set display resolution lock for mobile devices.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `enable` | `boolean` | Whether to enable resolution lock |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure

___

### setUninstallBlacklist

▸ **setUninstallBlacklist**(`packageNames`): `Promise`\<`OperationResult`\>

Set uninstall protection blacklist for mobile devices.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `packageNames` | `string`[] | List of Android package names to protect from uninstallation |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure

___

### startApp

▸ **startApp**(`startCmd`, `workDirectory?`, `activity?`): `Promise`\<`ProcessResult`\>

Start an app.

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `startCmd` | `string` | `undefined` |
| `workDirectory` | `string` | `''` |
| `activity` | `string` | `''` |

#### Returns

`Promise`\<`ProcessResult`\>

___

### stopAppByCmd

▸ **stopAppByCmd**(`stopCmd`): `Promise`\<`BoolResult`\>

Stop app by command.

#### Parameters

| Name | Type |
| :------ | :------ |
| `stopCmd` | `string` |

#### Returns

`Promise`\<`BoolResult`\>

___

### swipe

▸ **swipe**(`startX`, `startY`, `endX`, `endY`, `durationMs?`): `Promise`\<`BoolResult`\>

Swipe from one position to another on the mobile screen.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `startX` | `number` | `undefined` | Starting X coordinate |
| `startY` | `number` | `undefined` | Starting Y coordinate |
| `endX` | `number` | `undefined` | Ending X coordinate |
| `endY` | `number` | `undefined` | Ending Y coordinate |
| `durationMs` | `number` | `300` | Swipe duration in milliseconds. Default is 300 |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to BoolResult with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateSwipe() {
  try {
    const result = await agentBay.create({ imageId: 'mobile_latest' });
    if (result.success && result.session) {
      const session = result.session;

      // Swipe up gesture from (200, 400) to (200, 100)
      const swipeResult = await session.mobile.swipe(200, 400, 200, 100, 300);
      if (swipeResult.success) {
        console.log('Swipe gesture completed successfully');
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateSwipe().catch(console.error);
```

___

### tap

▸ **tap**(`x`, `y`): `Promise`\<`BoolResult`\>

Tap at specified coordinates on the mobile screen.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `x` | `number` | X coordinate for the tap |
| `y` | `number` | Y coordinate for the tap |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to BoolResult with success status

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });

async function demonstrateTap() {
  try {
    const result = await agentBay.create({ imageId: 'mobile_latest' });
    if (result.success && result.session) {
      const session = result.session;

      // Tap at coordinates (100, 100)
      const tapResult = await session.mobile.tap(100, 100);
      if (tapResult.success) {
        console.log('Tap executed successfully');
      } else {
        console.log(`Tap failed: ${tapResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateTap().catch(console.error);
```

## Best Practices

1. Verify element coordinates before tap operations
2. Use appropriate swipe durations for smooth gestures
3. Wait for UI elements to load before interaction
4. Take screenshots for verification and debugging
5. Handle app installation and uninstallation properly
6. Configure app whitelists/blacklists for security


## Related Resources

- [Session API Reference](../common-features/basics/session.md)

