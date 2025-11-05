# Class: Application

Handles application operations in the AgentBay cloud environment.

**`Deprecated`**

This module is deprecated. Use Computer or Mobile modules instead.
- For desktop applications, use session.computer
- For mobile applications, use session.mobile

## Table of contents

### Constructors

- [constructor](application.md#constructor)

### Methods

- [getInstalledApps](application.md#getinstalledapps)
- [getRunningProcesses](application.md#getrunningprocesses)
- [getVisibleApps](application.md#getvisibleapps)
- [listVisibleApps](application.md#listvisibleapps)
- [startApp](application.md#startapp)
- [stopAppByCmd](application.md#stopappbycmd)
- [stopAppByPID](application.md#stopappbypid)
- [stopAppByPName](application.md#stopappbypname)

## Constructors

### constructor

• **new Application**(`session`): [`Application`](application.md)

Initialize an Application object.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `session` | `Object` | The Session instance that this Application belongs to. |
| `session.callMcpTool` | (`toolName`: `string`, `args`: `any`) => `Promise`\<\{ `data`: `string` ; `errorMessage`: `string` ; `requestId`: `string` ; `success`: `boolean`  }\> | - |
| `session.getAPIKey` | () => `string` | - |
| `session.getClient` | () => ``Client`` | - |
| `session.getSessionId` | () => `string` | - |

#### Returns

[`Application`](application.md)

## Methods

### getInstalledApps

▸ **getInstalledApps**(`startMenu?`, `desktop?`, `ignoreSystemApps?`): `Promise`\<`InstalledAppListResult`\>

Get a list of installed applications.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `startMenu` | `boolean` | `false` | Whether to include start menu applications. |
| `desktop` | `boolean` | `true` | Whether to include desktop applications. |
| `ignoreSystemApps` | `boolean` | `true` | Whether to ignore system applications. |

#### Returns

`Promise`\<`InstalledAppListResult`\>

A promise that resolves to the list of installed applications.

**`Deprecated`**

Use session.computer.getInstalledApps() for desktop or session.mobile.getInstalledApps() for mobile instead.

___

### getRunningProcesses

▸ **getRunningProcesses**(): `Promise`\<`ProcessListResult`\>

Get a list of running processes.

#### Returns

`Promise`\<`ProcessListResult`\>

A promise that resolves to the list of running processes.

**`Deprecated`**

Use session.computer.getRunningProcesses() for desktop or session.mobile.getRunningProcesses() for mobile instead.

___

### getVisibleApps

▸ **getVisibleApps**(): `Promise`\<`InstalledAppListResult`\>

Get a list of visible applications.

#### Returns

`Promise`\<`InstalledAppListResult`\>

A promise that resolves to the list of visible applications.

**`Deprecated`**

Use session.computer.getVisibleApps() for desktop instead. This API is not available for mobile.

___

### listVisibleApps

▸ **listVisibleApps**(): `Promise`\<`ProcessListResult`\>

Returns a list of currently visible applications.
Corresponds to Python's list_visible_apps() method

#### Returns

`Promise`\<`ProcessListResult`\>

ProcessListResult with visible apps and requestId

**`Throws`**

Error if the operation fails.

___

### startApp

▸ **startApp**(`startCmd`, `workDirectory?`, `activity?`): `Promise`\<`ProcessListResult`\>

Start an application.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `startCmd` | `string` | `undefined` | The command to start the application. |
| `workDirectory` | `string` | `""` | The working directory for the application. |
| `activity` | `string` | `""` | The activity to start (for mobile applications). |

#### Returns

`Promise`\<`ProcessListResult`\>

A promise that resolves to the result of starting the application.

**`Deprecated`**

Use session.computer.startApp() for desktop or session.mobile.startApp() for mobile instead.

___

### stopAppByCmd

▸ **stopAppByCmd**(`cmd`): `Promise`\<`AppOperationResult`\>

Stop an application by command.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `cmd` | `string` | The command to stop the application. |

#### Returns

`Promise`\<`AppOperationResult`\>

A promise that resolves to the result of stopping the application.

**`Deprecated`**

Use session.computer.stopAppByCmd() for desktop or session.mobile.stopAppByCmd() for mobile instead.

___

### stopAppByPID

▸ **stopAppByPID**(`pid`): `Promise`\<`AppOperationResult`\>

Stops an application by process ID.
Corresponds to Python's stop_app_by_pid() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `pid` | `number` | The process ID to stop. |

#### Returns

`Promise`\<`AppOperationResult`\>

AppOperationResult with operation result and requestId

**`Throws`**

Error if the operation fails.

___

### stopAppByPName

▸ **stopAppByPName**(`pname`): `Promise`\<`AppOperationResult`\>

Stop an application by process name.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `pname` | `string` | The process name of the application to stop. |

#### Returns

`Promise`\<`AppOperationResult`\>

A promise that resolves to the result of stopping the application.

**`Deprecated`**

Use session.computer.stopAppByPName() for desktop or session.mobile.stopAppByPName() for mobile instead.
