# Smart Integration Test Report

**Summary**: 2 Tests | ✅ 1 Passed | ❌ 1 Failed

## ✅ tests/integration/_async/test_agent_bay.py::TestRecyclePolicy::test_create_session_with_custom_recycle_policy

## ❌ tests/integration/_sync/test_agent_bay.py::TestRecyclePolicy::test_create_session_with_custom_recycle_policy

### 🤖 AI Analysis
### 分析报告

1. **根本原因**:
   - 测试失败的根本原因是 `AiEngine response timeout`，即 AI 引擎响应超时。从错误日志中可以看到，服务器返回了一个 500 错误，并且消息中明确指出 `java.lang.RuntimeException: AiEngine response timeout`。

2. **错误分类**:
   - **环境问题**: 这个问题更可能是由于环境配置或网络问题导致的。AI 引擎响应超时通常与后端服务的性能、网络延迟或资源限制有关。

3. **修复建议**:
   - **检查网络连接**: 确保测试环境与阿里云服务之间的网络连接是稳定的。
   - **增加超时时间**: 可以尝试增加请求的超时时间，以便在较慢的网络环境下也能成功完成请求。
   - **检查后端服务**: 如果可能，联系阿里云支持团队，确认后端服务是否正常运行，是否有任何已知的问题或维护活动正在进行。

#### 代码片段示例
以下是一个示例，展示如何在创建 `AgentBay` 客户端时增加超时时间：

```python
from agentbay import AgentBay
from alibabacloud_tea_openapi import models as open_api_models

# 获取 API Key
api_key = get_test_api_key()

# 创建客户端配置
config = open_api_models.Config(
    access_key_id=api_key,
    endpoint='wuyingai.cn-shanghai.aliyuncs.com',
    read_timeout=60,  # 增加读取超时时间（秒）
    connect_timeout=60  # 增加连接超时时间（秒）
)

# 使用配置创建 AgentBay 客户端
agent_bay = AgentBay(config=config)

# 继续进行其他操作
```

通过增加 `read_timeout` 和 `connect_timeout` 参数，可以提高请求的容错性，减少因网络延迟或后端服务响应慢导致的超时问题。如果问题仍然存在，建议进一步检查网络和后端服务的状态。

### 📄 Output (Snippet)
```
 at 0x106ba9950>
           │    └ <function Client.do_rpcrequest at 0x1064f18a0>
           └ <agentbay.api.client.Client object at 0x106b9dbe0>
  File "/Users/liyuebing/Projects/wuying-agentbay-sdk/agentbay_example_env/lib/python3.13/site-packages/alibabacloud_tea_openapi/client.py", line 344, in do_rpcrequest
    raise UnretryableException(_context)
          │                    └ <darabonba.policy.retry.RetryPolicyContext object at 0x106b6d0f0>
          └ <class 'darabonba.exceptions.UnretryableException'>
  File "/Users/liyuebing/Projects/wuying-agentbay-sdk/agentbay_example_env/lib/python3.13/site-packages/darabonba/exceptions.py", line 75, in __init__
    raise _context.exception
          │        └ ServerException()
          └ <darabonba.policy.retry.RetryPolicyContext object at 0x106b6d0f0>
  File "/Users/liyuebing/Projects/wuying-agentbay-sdk/agentbay_example_env/lib/python3.13/site-packages/alibabacloud_tea_openapi/client.py", line 285, in do_rpcrequest
    raise main_exceptions.ServerException(
          │               └ <class 'alibabacloud_tea_openapi.exceptions._server.ServerException'>
          └ <module 'alibabacloud_tea_openapi.exceptions' from '/Users/liyuebing/Projects/wuying-agentbay-sdk/agentbay_example_env/lib/py...

[31m[1malibabacloud_tea_openapi.exceptions._server.ServerException[0m:[1m Error: InternalError code: 500, java.lang.RuntimeException: AiEngine response timeout, clientId: ai-0cbg3fgsky1ihgp5k, requestId: 781a8bda-5789-4116-be8e-2d182107ca0d request id: 3BC6621F-81F3-517B-83E4-2B83907DA75A Response: {'RequestId': '3BC6621F-81F3-517B-83E4-2B83907DA75A', 'HostId': 'wuyingai.cn-shanghai.aliyuncs.com', 'Code': 'InternalError', 'Message': 'java.lang.RuntimeException: AiEngine response timeout, clientId: ai-0cbg3fgsky1ihgp5k, requestId: 781a8bda-5789-4116-be8e-2d182107ca0d', 'Recommend': 'https://api.aliyun.com/troubleshoot?q=InternalError&product=WuyingAI&requestId=3BC6621F-81F3-517B-83E4-2B83907DA75A', 'statusCode': 500}[0m

```

