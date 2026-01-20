# Interface: CreateSessionParams

Parameters for creating a session.

## Table of contents

### Properties

- [betaNetworkId](#betanetworkid)
- [betaVolume](#betavolume)
- [betaVolumeId](#betavolumeid)
- [browserContext](#browsercontext)
- [contextSync](#contextsync)
- [enableBrowserReplay](#enablebrowserreplay)
- [extraConfigs](#extraconfigs)
- [framework](#framework)
- [imageId](#imageid)
- [labels](#labels)
- [policyId](#policyid)

## Properties

### betaNetworkId

• `Optional` **betaNetworkId**: `string`

___

### betaVolume

• `Optional` **betaVolume**: `string` \| ``Volume``

Beta: mount a volume during session creation (static mount).
Accepts a volume id string or a Volume object.

___

### betaVolumeId

• `Optional` **betaVolumeId**: `string`

Beta: explicit volume id mount during session creation.
If both betaVolume and betaVolumeId are provided, betaVolume takes precedence.

___

### browserContext

• `Optional` **browserContext**: ``BrowserContext``

___

### contextSync

• `Optional` **contextSync**: [`ContextSync`](context-sync.md)[]

___

### enableBrowserReplay

• `Optional` **enableBrowserReplay**: `boolean`

___

### extraConfigs

• `Optional` **extraConfigs**: ``ExtraConfigs``

___

### framework

• `Optional` **framework**: `string`

___

### imageId

• `Optional` **imageId**: `string`

___

### labels

• `Optional` **labels**: `Record`\<`string`, `string`\>

___

### policyId

• `Optional` **policyId**: `string`
