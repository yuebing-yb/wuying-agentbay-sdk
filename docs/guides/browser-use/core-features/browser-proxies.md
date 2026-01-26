# Browser Proxy Configuration Guide

---

## Overview

Browser Proxy is a core feature of the AgentBay SDK that enables developers to route browser traffic through proxy servers. This functionality is essential for scenarios requiring IP rotation, geographical distribution, or network anonymization. The AgentBay SDK supports both custom proxy servers and integrated Wuying Proxy Service.

## Key Features

### 1. Custom Proxy Support
Configure your own proxy servers with full control over routing and authentication:
- **Protocol Support**: HTTP, HTTPS, and SOCKS proxies
- **Authentication**: Optional username and password authentication
- **Flexible Configuration**: Support for various proxy server configurations

### 2. Wuying Proxy Service
Leverage Alibaba Cloud's integrated proxy service with advanced management features:
- **Restricted Strategy**: Uses fixed proxy nodes for consistent IP addresses
- **Polling Strategy**: Rotates through a pool of proxy nodes for IP diversity
- **Managed Infrastructure**: No need to maintain your own proxy servers

### 3. Managed Proxy Service
Use your own proxy resources with Wuying's intelligent management:
- **Bring Your Own Proxies**: Upload and manage your existing proxy infrastructure
- **Intelligent Allocation**: Multiple strategies for different use cases (polling, sticky, rotating, matched)
- **Health Monitoring**: Automatic health checks and failover
- **Geographic Filtering**: Select proxies by country, province, city, and ISP
- **User-based Management**: Maintain consistent or rotating IPs per user

> **📞 Getting Started with Managed Proxy**: Contact us or your account manager to set up your managed proxy pool.

## Proxy Types and Strategies

### Custom Proxy
Suitable for users who have their own proxy infrastructure or specific proxy requirements.

**Configuration Options:**
- `type`: Set to `"custom"`
- `server`: Proxy server address (required)
- `username`: Authentication username (optional)
- `password`: Authentication password (optional)

### Wuying Proxy
Provided by the Wuying Proxy Service integrated in AgentBay SDK

**Restricted Strategy:**
- Uses fixed proxy nodes
- Provides stable IP addresses
- The IP remains stable for the lifetime of the session.

**Polling Strategy:**
- Rotates through a pool of proxy nodes
- Provides IP diversity for each request
- Suitable for scenarios requiring frequent IP changes
- Configurable pool size via `pollsize` parameter

### Managed Proxy
Client-provided proxies managed by Wuying platform. This allows you to use your own proxy resources while leveraging Wuying's intelligent management capabilities.

> **📞 Contact Us**: To use managed proxy features, please contact us or reach out to your account manager to set up your proxy pool.

**Key Features:**
- **Centralized Management**: Upload and manage your proxy resources through Wuying platform
- **Intelligent Allocation**: Automatic proxy allocation based on your chosen strategy
- **Health Monitoring**: Automatic health checks and failover for your proxies
- **Flexible Strategies**: Multiple allocation strategies to fit different use cases

**Available Strategies:**

1. **Polling Strategy** (Pool-based, Round-robin)
   - Allocates one proxy per session from the pool
   - Round-robin selection ensures even distribution
   - `user_id`: Used for tracking allocation records, each session gets an independent allocation
   - Suitable for general purpose web scraping

2. **Sticky Strategy** (User-based, Consistent IP)
   - Keep the same IP for a specific user across sessions
   - `user_id`: Associates with historical allocations to maintain consistent IP
   - Ideal for maintaining session continuity per user

3. **Rotating Strategy** (User-based, Force New IP)
   - Force a different IP for a specific user each time
   - `user_id`: Associates with historical allocations to rotate through different IPs
   - Best for scenarios requiring IP diversity per user

4. **Matched Strategy** (Attribute-based Filtering)
   - Filter proxies by geographic and ISP attributes
   - `user_id`: Used for tracking allocation records, each session gets an independent allocation
   - Supports filtering by: ISP, country, province, city
   - Perfect for geo-targeted scraping or testing

**Configuration Parameters:**
- `proxy_type`: Set to `"managed"`
- `strategy`: One of `"polling"`, `"sticky"`, `"rotating"`, `"matched"`
- `user_id`: Custom user identifier for tracking proxy allocation records (**Required** for managed type)
  - `sticky`/`rotating` strategies: Associates with historical allocations to maintain or rotate IPs per user
  - `polling`/`matched` strategies: Each session gets an independent allocation
- `isp`: ISP filter (optional for matched strategy)
- `country`: Country filter (optional for matched strategy)
- `province`: Province filter (optional for matched strategy)
- `city`: City filter (optional for matched strategy)

## Python Implementation

### Basic Usage

```python
import os
from agentbay import AgentBay
from agentbay import CreateSessionParams
from agentbay import BrowserOption, BrowserProxy
from playwright.sync_api import sync_playwright

def main():
    """Main function demonstrating browser proxy functionality."""
    # Get API key from environment variable
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    print("Initializing AgentBay client...")
    agent_bay = AgentBay(api_key=api_key)

    print("Creating new session...")
    params = CreateSessionParams(
        image_id="browser_latest",  # Use latest browser image
    )
    session_result = agent_bay.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created successfully, Session ID: {session.session_id}")

        # ==================== Proxy Configuration Examples ====================
        
        # Example 1: Custom Proxy Configuration
        # Suitable for users who have their own proxy servers
        # browser_proxy = BrowserProxy(
        #     proxy_type="custom",           # Proxy type: custom
        #     server="http://127.0.0.1:9090", # Proxy server address (required)
        #     username="username",           # Proxy username (optional)
        #     password="password"            # Proxy password (optional)
        # )

        # Example 2: Wuying Proxy - Polling Strategy
        # Rotates through proxy pool nodes, suitable for scenarios requiring frequent IP switching
        browser_proxy = BrowserProxy(
            proxy_type="wuying",    # Proxy type: wuying proxy
            strategy="polling",     # Strategy: polling
            pollsize=2             # Proxy pool size: 2 nodes
        )

        # Example 3: Wuying Proxy - Restricted Strategy
        # Uses fixed proxy nodes, suitable for scenarios requiring stable IP
        # browser_proxy = BrowserProxy(
        #     proxy_type="wuying",    # Proxy type: wuying proxy
        #     strategy="restricted"   # Strategy: restricted (fixed nodes)
        # )

        # ==================== Managed Proxy Examples ====================
        # Note: To use managed proxy, please contact us first to set up your proxy pool
        
        # Example 4: Managed Proxy - Polling Strategy
        # Pool-based allocation, round-robin selection
        # browser_proxy = BrowserProxy(
        #     proxy_type="managed",   # Proxy type: managed proxy
        #     strategy="polling",     # Strategy: polling (round-robin)
        #     user_id="user123"       # REQUIRED: custom user identifier (independent allocation per session)
        # )
        
        # Example 5: Managed Proxy - Sticky Strategy
        # User-based allocation, keep same IP for specific user
        # browser_proxy = BrowserProxy(
        #     proxy_type="managed",   # Proxy type: managed proxy
        #     strategy="sticky",      # Strategy: sticky (consistent IP per user)
        #     user_id="user123"       # REQUIRED: custom user identifier (associates with historical allocations)
        # )
        
        # Example 6: Managed Proxy - Rotating Strategy
        # User-based allocation, force different IP for specific user
        # browser_proxy = BrowserProxy(
        #     proxy_type="managed",   # Proxy type: managed proxy
        #     strategy="rotating",    # Strategy: rotating (new IP per request)
        #     user_id="user123"       # REQUIRED: custom user identifier (rotates from historical allocations)
        # )
        
        # Example 7: Managed Proxy - Matched Strategy
        # Attribute-based filtering, select proxies by location/ISP
        # browser_proxy = BrowserProxy(
        #     proxy_type="managed",   # Proxy type: managed proxy
        #     strategy="matched",     # Strategy: matched (attribute filtering)
        #     user_id="user123",      # REQUIRED: custom user identifier (independent allocation per session)
        #     isp="China Telecom",    # Filter by ISP (optional)
        #     country="China",        # Filter by country (optional)
        #     province="Beijing",     # Filter by province (optional)
        #     city="Beijing"          # Filter by city (optional)
        # )

        # Create browser options with proxy configuration, now only support one proxy
        browser_option = BrowserOption(
            proxies=[browser_proxy]
        )

        # Initialize browser instance
        if session.browser.initialize(browser_option):
            # Get browser CDP connection endpoint
            endpoint_url = session.browser.get_endpoint_url()
            print(f"Browser CDP endpoint: {endpoint_url}")

            # Use Playwright to connect to remote browser instance
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]  # Get default browser context
                page = context.new_page()  # Create new page

                # ==================== Verify Proxy IP ====================
                print("\n--- Starting proxy public IP check ---")
                page.goto("https://httpbin.org/ip")  # Visit IP checking service

                try:
                    # Parse JSON response from page content
                    response = page.evaluate("() => JSON.parse(document.body.textContent)")
                    public_ip = response.get("origin", "").strip()
                    print(f"Proxy public IP: {public_ip}")
                except Exception as e:
                    print(f"Failed to get proxy public IP: {e}")
                    public_ip = None
                print("--- Proxy IP check completed ---\n")
                
                # Wait 3 seconds to observe results
                page.wait_for_timeout(3000)
                browser.close()
        else:
            print("Browser initialization failed")

        # Clean up session resources
        print("Cleaning up session...")
        agent_bay.delete(session)
        print("Session cleanup completed")


if __name__ == "__main__":
    main()
```

## TypeScript Implementation

### Basic Usage

```typescript
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';
import { BrowserOption, BrowserProxy } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';

interface IpResponse {
    origin: string;
}

async function proxyExample(): Promise<void> {
    // Initialize AgentBay client
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
        console.log('Error: AGENTBAY_API_KEY environment variable not set');
        return;
    }

    try {
        const agentBay = new AgentBay({ apiKey });

        // Create a session
        const params: CreateSessionParams = {
            imageId: 'browser_latest',
        };
        const sessionResult = await agentBay.create(params);

        if (!sessionResult.success) {
            console.log('Failed to create session');
            return;
        }

        const session = sessionResult.session;
        console.log(`Session created with ID: ${session.sessionId}`);

        // Example 1: Custom Proxy Configuration
        // const browserProxy: BrowserProxy = {
        //     type: 'custom',
        //     server: 'http://127.0.0.1:9090',
        //     username: 'username',
        //     password: 'password',
        //     toMap: function() {
        //         return {
        //             type: this.type,
        //             server: this.server,
        //             username: this.username,
        //             password: this.password
        //         };
        //     }
        // };

        // Example 2: Wuying Proxy - Polling Strategy
        const browserProxy: BrowserProxy = {
            type: 'wuying',
            strategy: 'polling',
            pollsize: 2,
            toMap: function() {
                return {
                    type: this.type,
                    strategy: this.strategy,
                    pollsize: this.pollsize
                };
            }
        };

        // Example 3: Wuying Proxy - Restricted Strategy
        // const browserProxy: BrowserProxy = {
        //     type: 'wuying',
        //     strategy: 'restricted',
        //     toMap: function() {
        //         return {
        //             type: this.type,
        //             strategy: this.strategy
        //         };
        //     }
        // };

        // ==================== Managed Proxy Examples ====================
        // Note: To use managed proxy, please contact us first to set up your proxy pool
        
        // Example 4: Managed Proxy - Polling Strategy
        // const browserProxy: BrowserProxy = {
        //     type: 'managed',
        //     strategy: 'polling',
        //     userId: 'user123',  // REQUIRED: custom user identifier (independent allocation per session)
        //     toMap: function() {
        //         return {
        //             type: this.type,
        //             strategy: this.strategy,
        //             userId: this.userId
        //         };
        //     }
        // };
        
        // Example 5: Managed Proxy - Sticky Strategy
        // const browserProxy: BrowserProxy = {
        //     type: 'managed',
        //     strategy: 'sticky',
        //     userId: 'user123',  // REQUIRED: custom user identifier (associates with historical allocations)
        //     toMap: function() {
        //         return {
        //             type: this.type,
        //             strategy: this.strategy,
        //             userId: this.userId
        //         };
        //     }
        // };
        
        // Example 6: Managed Proxy - Rotating Strategy
        // const browserProxy: BrowserProxy = {
        //     type: 'managed',
        //     strategy: 'rotating',
        //     userId: 'user123',  // REQUIRED: custom user identifier (rotates from historical allocations)
        //     toMap: function() {
        //         return {
        //             type: this.type,
        //             strategy: this.strategy,
        //             userId: this.userId
        //         };
        //     }
        // };
        
        // Example 7: Managed Proxy - Matched Strategy
        // const browserProxy: BrowserProxy = {
        //     type: 'managed',
        //     strategy: 'matched',
        //     userId: 'user123',  // REQUIRED: custom user identifier (independent allocation per session)
        //     isp: 'China Telecom',
        //     country: 'China',
        //     province: 'Beijing',
        //     city: 'Beijing',
        //     toMap: function() {
        //         return {
        //             type: this.type,
        //             strategy: this.strategy,
        //             userId: this.userId,
        //             isp: this.isp,
        //             country: this.country,
        //             province: this.province,
        //             city: this.city
        //         };
        //     }
        // };

        // Create browser option with proxy configuration
        const browserOption: BrowserOption = {
            proxies: [browserProxy]
        };

        const initialized = await session.browser.initializeAsync(browserOption);
        if (initialized) {
            const endpointUrl = session.browser.getEndpointUrl();
            console.log('endpoint_url =', endpointUrl);

            const browser = await chromium.connectOverCDP(endpointUrl);
            const context = browser.contexts()[0];
            const page = await context.newPage();

            try {
                // Verify proxy IP
                console.log('\n--- Check proxy public IP start ---');
                await page.goto('https://httpbin.org/ip');

                const response = await page.evaluate((): IpResponse => {
                    return JSON.parse(document.body.textContent || '{}');
                });
                const publicIp = response.origin || '';
                console.log('proxy public IP:', publicIp);
                console.log('--- Check proxy public IP end ---');

                await page.waitForTimeout(3000);
            } finally {
                await browser.close();
            }
        }

        // Clean up session
        await agentBay.delete(session);
    } catch (error) {
        console.error('Error:', error);
    }
}

proxyExample().catch(console.error);
```

## Managed Proxy Deep Dive

### What is Managed Proxy?

Managed Proxy allows you to use your own proxy resources while benefiting from Wuying's intelligent management platform. Instead of maintaining complex proxy allocation logic in your code, you simply upload your proxies to Wuying, and the platform handles:

- **Automatic allocation** based on your chosen strategy
- **Health monitoring** with automatic failover
- **Load balancing** across your proxy pool
- **Geographic filtering** for location-specific requirements
- **User session management** for consistent user experiences

### Getting Started

#### Step 1: Contact Us for Setup

Before using managed proxy, you need to set up your proxy pool with our team:

1. **Contact Support**: Reach out to us or your account manager
2. **Provide Proxy Details**: Share your proxy list with the following information:
   - Proxy server addresses (IP:Port)
   - Authentication credentials (if required)
   - Geographic information (country, province, city)
   - ISP information (e.g., China Telecom, China Unicom)
3. **Configure Pool**: Our team will help you configure your managed proxy pool
4. **Get Pool ID**: You'll receive a pool identifier to use in your code

#### Step 2: Choose Your Strategy

Select the strategy that best fits your use case:

| Strategy | Best For | Use Case |
|----------|----------|----------|
| **Polling** | General purpose | Web scraping with even load distribution |
| **Sticky** | User consistency | Maintaining login sessions per user |
| **Rotating** | Maximum diversity | Aggressive scraping to avoid detection |
| **Matched** | Geographic targeting | Testing region-specific content |

**Polling Strategy** - General Purpose
```python
# Best for: Even distribution, general web scraping
BrowserProxy(
    proxy_type="managed",
    strategy="polling"
)
```
- Round-robin selection from your proxy pool
- Each session gets a different proxy
- Simple and effective for most use cases

**Sticky Strategy** - User Consistency
```python
# Best for: Maintaining user sessions, login persistence
BrowserProxy(
    proxy_type="managed",
    strategy="sticky",
    user_id="user123"  # Same user_id = same proxy
)
```
- Same user always gets the same proxy
- Perfect for maintaining login sessions
- Useful for user-specific testing

**Rotating Strategy** - Maximum Diversity
```python
# Best for: Avoiding detection, maximum IP diversity
BrowserProxy(
    proxy_type="managed",
    strategy="rotating",
    user_id="user123"  # Same user_id = different proxy each time
)
```
- Same user gets a different proxy each time
- Maximum IP diversity per user
- Ideal for aggressive scraping scenarios

**Matched Strategy** - Geographic Targeting
```python
# Best for: Location-specific content, geo-testing
BrowserProxy(
    proxy_type="managed",
    strategy="matched",
    country="China",
    province="Beijing",
    isp="China Telecom"
)
```
- Filter proxies by location and ISP
- Perfect for testing region-specific features
- Ideal for accessing geo-restricted content

### Use Cases and Examples

#### Use Case 1: E-commerce Price Monitoring
Monitor prices across different regions:

```python
# Monitor prices from different cities
beijing_proxy = BrowserProxy(
    proxy_type="managed",
    strategy="matched",
    country="China",
    province="Beijing"
)

shanghai_proxy = BrowserProxy(
    proxy_type="managed",
    strategy="matched",
    country="China",
    province="Shanghai"
)
```

#### Use Case 2: User Session Testing
Test multi-user scenarios with consistent IPs:

```python
# User A always gets the same IP
user_a_proxy = BrowserProxy(
    proxy_type="managed",
    strategy="sticky",
    user_id="user_a"
)

# User B always gets the same IP (different from A)
user_b_proxy = BrowserProxy(
    proxy_type="managed",
    strategy="sticky",
    user_id="user_b"
)
```

#### Use Case 3: Large-scale Web Scraping
Maximize IP diversity to avoid rate limiting:

```python
# Each request uses a different proxy
scraping_proxy = BrowserProxy(
    proxy_type="managed",
    strategy="polling"  # Round-robin through all proxies
)
```

### Monitoring and Debugging

When using managed proxy, you can verify the proxy is working correctly:

```python
# Check the current proxy IP
page.goto("https://httpbin.org/ip")
response = page.evaluate("() => JSON.parse(document.body.textContent)")
current_ip = response.get("origin", "")
print(f"Current proxy IP: {current_ip}")

# Check geographic location
page.goto("https://ipapi.co/json/")
geo_info = page.evaluate("() => JSON.parse(document.body.textContent)")
print(f"Location: {geo_info.get('city')}, {geo_info.get('country_name')}")
print(f"ISP: {geo_info.get('org')}")
```

### Common Questions

**Q: Do I need my own proxies?**  
A: Yes, managed proxy is for using your existing proxy infrastructure with our management platform.

**Q: How long does setup take?**  
A: Typically 1-2 business days after providing your proxy list.

**Q: Can I update my proxy list later?**  
A: Yes, contact us to update your proxy pool at any time.

**Q: What if a proxy goes down?**  
A: Our platform automatically detects unhealthy proxies and removes them from rotation.

**Q: Can I mix strategies?**  
A: Currently, one strategy per session. Different sessions can use different strategies.

### Comparison: Managed vs Wuying vs Custom

| Feature | Custom | Wuying | Managed |
|---------|--------|--------|---------|
| **Setup Required** | None | None | Yes (Contact Us) |
| **Own Proxies** | ✅ | ❌ | ✅ |
| **Health Monitoring** | ❌ | ✅ | ✅ |
| **Geographic Filtering** | ❌ | ❌ | ✅ |
| **User-based Allocation** | ❌ | ❌ | ✅ |
| **Automatic Failover** | ❌ | ✅ | ✅ |
| **Pool Management** | Manual | Automatic | Automatic |

## Best Practices

### 1. Proxy Selection Strategy

**Custom Proxy Usage:**
- Use when you have existing proxy infrastructure
- Ideal for specific geographic requirements
- Provides full control over proxy configuration

```python
# ✅ Correct - Custom proxy with authentication
custom_proxy = BrowserProxy(
    proxy_type="custom",
    server="http://proxy.example.com:8080",
    username="your_username",
    password="your_password"
)
```

**Wuying Proxy Usage:**
- Use for managed proxy infrastructure
- Choose strategy based on your use case:
  - **Restricted**: For consistent IP requirements
  - **Polling**: For IP rotation needs

```python
# ✅ Correct - Wuying proxy with appropriate strategy
wuying_proxy = BrowserProxy(
    proxy_type="wuying",
    strategy="polling",
    pollsize=3  # Adjust based on your needs
)
```

**Managed Proxy Usage:**
- Contact us first to set up your proxy pool
- Choose strategy based on your requirements:
  - **Polling**: General purpose, even distribution
  - **Sticky**: Maintain user sessions with consistent IPs
  - **Rotating**: Maximum IP diversity per user
  - **Matched**: Geographic or ISP-specific requirements

```python
# ✅ Correct - Managed proxy with user-based strategy
managed_proxy = BrowserProxy(
    proxy_type="managed",
    strategy="sticky",
    user_id="user123"  # Required for user-based strategies
)

# ✅ Correct - Managed proxy with geographic filtering
managed_proxy = BrowserProxy(
    proxy_type="managed",
    strategy="matched",
    country="China",
    province="Beijing",
    isp="China Telecom"
)
```

### 2. Error Handling and Monitoring

```python
def robust_proxy_usage():
    try:
        # Initialize browser with proxy
        if session.browser.initialize(browser_option):
            endpoint_url = session.browser.get_endpoint_url()
            
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = context.new_page()
                
                # Verify proxy is working
                page.goto("https://httpbin.org/ip", timeout=30000)
                
                # Check if proxy is applied
                response = page.evaluate("() => JSON.parse(document.body.textContent)")
                proxy_ip = response.get("origin", "").strip()
                
                if not proxy_ip:
                    raise Exception("Failed to detect proxy IP")
                    
                print(f"Successfully using proxy IP: {proxy_ip}")
                
                browser.close()
        else:
            print("Browser initialization failed - check proxy configuration")
            
    except Exception as e:
        print(f"Proxy configuration error: {e}")
        # Implement fallback logic or retry mechanism
```

## Limitations
- **Single Proxy Support**: Although BrowserOption accepts an array in proxies, only the first proxy is currently applied per session.
- **Global Proxy Scope**: The proxy applies globally, meaning all browser requests will be routed through the proxy
- **Managed Proxy Setup**: Managed proxy requires prior setup. Contact us to configure your proxy pool before use

## 📚 Related Guides

- [Browser Context](browser-context.md) - Browser context management for cookies and sessions
- [Browser Fingerprint](browser-fingerprint.md) - Simulate browser fingerprint for web automation
- [Browser Use Overview](../README.md) - Complete browser automation features
- [Session Management](../../common-features/basics/session-management.md) - Session lifecycle and configuration

## 🆘 Getting Help

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation Home](../../README.md)
