# Class: Code

## 💻 Related Tutorial

- [Code Execution Guide](../../../../docs/guides/codespace/code-execution.md) - Execute code in isolated environments

## Overview

The Code module provides secure code execution capabilities in isolated environments.
It supports multiple programming languages including Python, JavaScript, and more.


## Requirements

- Requires `code_latest` image for code execution features

Handles code execution operations in the AgentBay cloud environment.

## Table of contents


### Methods

- [runCode](code.md#runcode)

## Methods

### runCode

▸ **runCode**(`code`, `language`, `timeoutS?`): `Promise`\<`CodeExecutionResult`\>

Execute code in the specified language with a timeout.
Corresponds to Python's run_code() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `code` | `string` | `undefined` | The code to execute. |
| `language` | `string` | `undefined` | The programming language of the code. Must be either 'python' or 'javascript'. |
| `timeoutS` | `number` | `60` | The timeout for the code execution in seconds. Default is 60s. Note: Due to gateway limitations, each request cannot exceed 60 seconds. |

#### Returns

`Promise`\<`CodeExecutionResult`\>

CodeExecutionResult with code execution output and requestId

**`Throws`**

Error if an unsupported language is specified.

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateCodeExecution() {
    try {
        // Create a session with code_latest image
        const result = await agentBay.create({ imageId: "code_latest" });
        if (result.success) {
            const session = result.session;

            // Execute Python code
            const pythonCode = `
print("Hello from Python!")
result = 2 + 3
print(f"Result: {result}")
`;
            const codeResult = await session.code.runCode(pythonCode, "python");
            if (codeResult.success) {
                console.log(`Python output:\n${codeResult.result}`);
            }

            // Execute JavaScript code
            const jsCode = `
console.log("Hello from JavaScript!");
const result = 2 + 3;
console.log("Result:", result);
`;
            const jsResult = await session.code.runCode(jsCode, "javascript", 30);
            if (jsResult.success) {
                console.log(`JavaScript output:\n${jsResult.result}`);
            }

            await session.delete();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

demonstrateCodeExecution().catch(console.error);
```

## Best Practices

1. Validate code syntax before execution
2. Set appropriate execution timeouts
3. Handle execution errors and exceptions
4. Use proper resource limits to prevent resource exhaustion
5. Clean up temporary files after code execution


## Related Resources

- [Session API Reference](../common-features/basics/session.md)

