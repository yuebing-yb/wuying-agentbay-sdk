# Interface: CreateSessionParams

Parameters for creating a session.

## Table of contents

### Properties

- [betaNetworkId](#betanetworkid)
- [browserContext](#browsercontext)
- [contextSync](#contextsync)
- [enableBrowserReplay](#enablebrowserreplay)
- [extraConfigs](#extraconfigs)
- [framework](#framework)
- [imageId](#imageid)
- [labels](#labels)
- [policyId](#policyid)
- [volume](#volume)
- [volumeId](#volumeid)

## Properties

### betaNetworkId

• `Optional` **betaNetworkId**: `string`

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

___

### volume

• `Optional` **volume**: `string` \| ``Volume``

Beta: mount a volume during session creation (static mount).
Accepts a volume id string or a Volume object.

___

### volumeId

• `Optional` **volumeId**: `string`

Beta: explicit volume id mount during session creation.
If both volume and volumeId are provided, volume takes precedence.
