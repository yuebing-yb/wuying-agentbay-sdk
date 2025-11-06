# Class: Mobile

## 📱 Related Tutorial

- [Mobile Use Guide](../../../../../docs/guides/mobile-use/README.md) - Automate mobile applications

## Table of contents

### Constructors

- [constructor](mobile.md#constructor)

### Methods

- [configure](mobile.md#configure)
- [getAdbUrl](mobile.md#getadburl)
- [getAllUIElements](mobile.md#getalluielements)
- [getClickableUIElements](mobile.md#getclickableuielements)
- [getInstalledApps](mobile.md#getinstalledapps)
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

## Constructors

### constructor

• **new Mobile**(`session`): [`Mobile`](mobile.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `session` | `MobileSession` |

#### Returns

[`Mobile`](mobile.md)

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

___

### getAdbUrl

▸ **getAdbUrl**(`adbkeyPub`): `Promise`\<`AdbUrlResult`\>

Retrieves the ADB connection URL for the mobile environment.
This method is only supported in mobile environments (mobile_latest image).
It uses the provided ADB public key to establish the connection and returns
the ADB connect URL.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `adbkeyPub` | `string` | ADB public key for authentication |

#### Returns

`Promise`\<`AdbUrlResult`\>

AdbUrlResult containing the ADB connection URL

___

### getAllUIElements

▸ **getAllUIElements**(`timeoutMs?`): `Promise`\<`UIElementsResult`\>

Get all UI elements.

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `timeoutMs` | `number` | `3000` |

#### Returns

`Promise`\<`UIElementsResult`\>

___

### getClickableUIElements

▸ **getClickableUIElements**(`timeoutMs?`): `Promise`\<`UIElementsResult`\>

Get clickable UI elements.

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `timeoutMs` | `number` | `5000` |

#### Returns

`Promise`\<`UIElementsResult`\>

___

### getInstalledApps

▸ **getInstalledApps**(`startMenu?`, `desktop?`, `ignoreSystemApps?`): `Promise`\<`InstalledAppsResult`\>

Get installed apps.

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `startMenu` | `boolean` | `false` |
| `desktop` | `boolean` | `true` |
| `ignoreSystemApps` | `boolean` | `true` |

#### Returns

`Promise`\<`InstalledAppsResult`\>

___

### inputText

▸ **inputText**(`text`): `Promise`\<`BoolResult`\>

Input text.

#### Parameters

| Name | Type |
| :------ | :------ |
| `text` | `string` |

#### Returns

`Promise`\<`BoolResult`\>

___

### screenshot

▸ **screenshot**(): `Promise`\<`ScreenshotResult`\>

Take a screenshot.

#### Returns

`Promise`\<`ScreenshotResult`\>

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

Swipe from one position to another.

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `startX` | `number` | `undefined` |
| `startY` | `number` | `undefined` |
| `endX` | `number` | `undefined` |
| `endY` | `number` | `undefined` |
| `durationMs` | `number` | `300` |

#### Returns

`Promise`\<`BoolResult`\>

___

### tap

▸ **tap**(`x`, `y`): `Promise`\<`BoolResult`\>

Tap at specified coordinates.

#### Parameters

| Name | Type |
| :------ | :------ |
| `x` | `number` |
| `y` | `number` |

#### Returns

`Promise`\<`BoolResult`\>

## Related Resources

- [Session API Reference](../common-features/basics/session.md)

