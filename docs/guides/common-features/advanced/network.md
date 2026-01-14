# Network (Beta)

The Network feature provides **network redirection** between your local environment and the AgentBay cloud runtime. It allows a cloud session to use your local network egress, which can help reduce risk-control issues in certain websites or mobile apps.

## When to use it

- **Local egress requirement**: a target website/app only works reliably from your local network
- **IP / network reputation sensitivity**: you want the cloud runtime traffic to appear as local traffic
- **Connectivity constraints**: you need the cloud runtime to access resources reachable only from your local network

## How it works

1. Create (or reuse) a network and obtain a `networkId` and a `networkToken`.
2. Bind the `networkToken` in your local environment by running the CLI tool.
3. Poll the network status until it is ready.
4. Create a session and bind it to the `networkId` for redirection.

## Usage workflow

### 1) Create a network and get bind token

```python
import os
from agentbay import AgentBay

agent = AgentBay(api_key=os.environ["AGENTBAY_API_KEY"])
net = agent.beta_network.get_network_bind_token()
if not net.success:
    raise RuntimeError(net.error_message)

network_id = net.network_id
network_token = net.network_token
```

### 2) Bind the token in your local environment

Run the following command in a local terminal:

```bash
./rick-cli -m bind -t <network-token>
```

### 3) Check network readiness

```python
import time

max_wait_s = 120
deadline = time.time() + max_wait_s
while True:
    status = agent.beta_network.describe(network_id)
    if not status.success:
        raise RuntimeError(status.error_message)
    if status.online:
        break
    if time.time() > deadline:
        raise TimeoutError("Network is not ready")
    time.sleep(2)
```

### 4) Create a session bound to the network

```python
from agentbay import CreateSessionParams

params = CreateSessionParams(
    image_id="imgc-12345678",
    beta_network_id=network_id,
)

create = agent.create(params)
if not create.success:
    raise RuntimeError(create.error_message)

session = create.session
try:
    # Your automation code here.
    pass
finally:
    session.delete()
```

## Best practices

1. Keep `networkToken` secure. Do not commit it to source control.
2. Ensure the local binding process stays running and reachable while the session is active.
3. Always check the network status before creating sessions bound to it.
4. Use a dedicated custom image when required by your environment policy.

