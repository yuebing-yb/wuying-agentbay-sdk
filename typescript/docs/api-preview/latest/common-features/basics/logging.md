# Interface: LoggerConfig

## 📝 Related Tutorial

- [Logging Configuration Guide](../../../../../../docs/guides/common-features/configuration/logging.md) - Configure logging for the SDK

Logger configuration options

**`Example`**

```typescript
import { AgentBay, setupLogger } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateLogging() {
    try {
        // Configure logging with file output
        setupLogger({
            level: 'DEBUG',
            logFile: '/var/log/agentbay.log',
            maxFileSize: '100 MB',
            enableConsole: true
        });

        // Create a session - logs will be written to both console and file
        const result = await agentBay.create();
        if (result.success) {
            const session = result.session;
            console.log(`Session created: ${session.sessionId}`);
            await session.delete();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

demonstrateLogging().catch(console.error);
```

## Table of contents

### Properties

- `enableConsole`
- `level`
- `logFile`
- `maxFileSize`

## Properties

### enableConsole

• `Optional` **enableConsole**: `boolean`

___

### level

• `Optional` **level**: ``LogLevel``

___

### logFile

• `Optional` **logFile**: `string`

___

### maxFileSize

• `Optional` **maxFileSize**: `string`

## Related Resources

- [AgentBay API Reference](agentbay.md)

