# Code API Reference

## 💻 Related Tutorial

- [Code Execution Guide](../../../../../docs/guides/codespace/code-execution.md) - Execute code in isolated environments

## Overview

The Code module provides secure code execution capabilities in isolated environments.
It supports multiple programming languages including Python, JavaScript, and more.


## Requirements

- Requires `code_latest` image for code execution features



```python
logger = get_logger("code")
```

## CodeExecutionResult Objects

```python
class CodeExecutionResult(ApiResponse)
```

Result of code execution operations.

## Code Objects

```python
class Code(BaseService)
```

Handles code execution operations in the AgentBay cloud environment.

#### run\_code

```python
def run_code(code: str,
             language: str,
             timeout_s: int = 60) -> CodeExecutionResult
```

Execute code in the specified language with a timeout.

**Arguments**:

- `code` - The code to execute.
- `language` - The programming language of the code. Must be either 'python'
  or 'javascript'.
- `timeout_s` - The timeout for the code execution in seconds. Default is 60s.
- `Note` - Due to gateway limitations, each request cannot exceed 60 seconds.
  

**Returns**:

- `CodeExecutionResult` - Result object containing success status, execution
  result, and error message if any.
  

**Raises**:

- `CommandError` - If the code execution fails or if an unsupported language is
  specified.
  
  Important:
  The `run_code` method requires a session created with the `code_latest`
  image to function properly. If you encounter errors indicating that the
  tool is not found, make sure to create your session with
  `image_id="code_latest"` in the `CreateSessionParams`.
  

**Example**:

  Execute Python and JavaScript code in a code execution environment::
  
  from agentbay import AgentBay
  from agentbay.session_params import CreateSessionParams
  
  agent_bay = AgentBay(api_key="your_api_key")
  
  def execute_code_example():
  try:
  # Create a session with code_latest image
  params = CreateSessionParams(image_id="code_latest")
  session_result = agent_bay.create(params)
  if not session_result.success:
  print(f"Failed to create session: {session_result.error_message}")
  return
  
  session = session_result.session
  
  # Execute Python code
  python_code = """
  print("Hello from Python!")
  result = 2 + 3
- `print(f"Result` - {result}")
  """
  
  code_result = session.code.run_code(python_code, "python")
  if code_result.success:
  print(f"Python code output:\n{code_result.result}")
  # Expected output:
  # Hello from Python!
  # Result: 5
  else:
  print(f"Code execution failed: {code_result.error_message}")
  
  # Execute JavaScript code
  js_code = """
  console.log("Hello from JavaScript!");
  const result = 2 + 3;
  console.log("Result:", result);
  """
  
  js_result = session.code.run_code(js_code, "javascript", timeout_s=30)
  if js_result.success:
  print(f"JavaScript code output:\n{js_result.result}")
  # Expected output:
  # Hello from JavaScript!
  # Result: 5
  else:
  print(f"Code execution failed: {js_result.error_message}")
  
  session.delete()
  except Exception as e:
- `print(f"Error` - {e}")
  
  execute_code_example()

## Best Practices

1. Validate code syntax before execution
2. Set appropriate execution timeouts
3. Handle execution errors and exceptions
4. Use proper resource limits to prevent resource exhaustion
5. Clean up temporary files after code execution

## Related Resources

- [Session API Reference](../common-features/basics/session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
