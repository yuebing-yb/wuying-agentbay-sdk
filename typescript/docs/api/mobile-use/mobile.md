# Class: Mobile

## 📱 Related Tutorial

- [Mobile Use Guide](../../../../docs/guides/mobile-use/README.md) - Automate mobile applications

## Overview

The Mobile module provides mobile device automation capabilities including touch gestures,
text input, app management, and screenshot capture. It supports Android device automation.


## Requirements

- Requires `mobile_latest` image for mobile automation features

## Table of contents


### Methods

- [betaTakeLongScreenshot](#betatakelongscreenshot)
- [betaTakeScreenshot](#betatakescreenshot)
- [configure](#configure)
- [inputText](#inputtext)
- [screenshot](#screenshot)
- [sendKey](#sendkey)
- [setAppBlacklist](#setappblacklist)
- [setAppWhitelist](#setappwhitelist)
- [setNavigationBarVisibility](#setnavigationbarvisibility)
- [setResolutionLock](#setresolutionlock)
- [setUninstallBlacklist](#setuninstallblacklist)
- [startApp](#startapp)
- [stopAppByCmd](#stopappbycmd)
- [swipe](#swipe)
- [tap](#tap)

## Methods

### betaTakeLongScreenshot

▸ **betaTakeLongScreenshot**(`maxScreens?`, `format?`, `quality?`): `Promise`\<`BetaScreenshotResult`\>

Capture a long screenshot and return raw image bytes.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `maxScreens` | `number` | `4` | Number of screens to stitch (range: [2, 10]) |
| `format` | `string` | `"png"` | Output image format ("png", "jpeg", or "jpg"). Default is "png" |
| `quality?` | `number` | `undefined` | JPEG quality (range: [1, 100]) |

#### Returns

`Promise`\<`BetaScreenshotResult`\>

___

### betaTakeScreenshot

▸ **betaTakeScreenshot**(): `Promise`\<`BetaScreenshotResult`\>

Capture the current screen as a PNG image and return raw image bytes.

#### Returns

`Promise`\<`BetaScreenshotResult`\>

Promise resolving to BetaScreenshotResult containing PNG bytes

___

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
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const inputResult = await result.session.mobile.inputText('Hello Mobile');
  console.log('Text input successfully:', inputResult.success);
  await result.session.delete();
}
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
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const screenshotResult = await result.session.mobile.screenshot();
  console.log('Screenshot URL:', screenshotResult.data);
  await result.session.delete();
}
```

___

### sendKey

▸ **sendKey**(`key`): `Promise`\<`BoolResult`\>

Send Android key code.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `key` | `number` | Android key code (e.g., 4 for BACK, 3 for HOME, 24 for VOLUME_UP) |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to BoolResult with success status

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const keyResult = await result.session.mobile.sendKey(4);
  console.log('BACK key sent:', keyResult.success);
  await result.session.delete();
}
```

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

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `startCmd` | `string` | `undefined` | Start command using "monkey -p" format (e.g., 'monkey -p com.android.settings') |
| `workDirectory` | `string` | `''` | Optional working directory for the app |
| `activity` | `string` | `''` | Optional activity name to launch |

#### Returns

`Promise`\<`ProcessResult`\>

Promise resolving to ProcessResult containing launched process information

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const startResult = await result.session.mobile.startApp('monkey -p com.android.settings');
  console.log('App started:', startResult.success);
  await result.session.delete();
}
```

___

### stopAppByCmd

▸ **stopAppByCmd**(`stopCmd`): `Promise`\<`BoolResult`\>

Stop app by command.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `stopCmd` | `string` | Package name of the app to stop (e.g., 'com.android.settings') |

#### Returns

`Promise`\<`BoolResult`\>

Promise resolving to BoolResult with success status

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  await result.session.mobile.startApp('monkey -p com.android.settings');
  const stopResult = await result.session.mobile.stopAppByCmd('com.android.settings');
  console.log('App stopped:', stopResult.success);
  await result.session.delete();
}
```

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
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const swipeResult = await result.session.mobile.swipe(200, 400, 200, 100, 300);
  console.log('Swipe success:', swipeResult.success);
  await result.session.delete();
}
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
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const tapResult = await result.session.mobile.tap(100, 100);
  console.log('Tap success:', tapResult.success);
  await result.session.delete();
}
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

