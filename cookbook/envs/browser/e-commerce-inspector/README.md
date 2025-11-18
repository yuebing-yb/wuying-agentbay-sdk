# E-commerce Inspector Agent

This project demonstrates how to create an e-commerce inspector agent using the AgentBay SDK. The agent can automatically visit e-commerce websites, navigate to product listing pages, extract product information (names, prices, links), and save the results with screenshots.

## What It Does

**Input:** A URL to an e-commerce product listing page
```
https://waydoo.com/collections/all
```

**Output:** Structured product data + Screenshot

<table>
<tr>
<td width="50%">

**Screenshot of Product Listing Page**

![Product Listing Page](./assets/waydoo_screenshot.png)

</td>
<td width="50%">

**Extracted Product Information (JSON)**

```json
[
  {
    "name": "15L Waterproof Dry Bag Backpack",
    "price": "$22.90",
    "link": "/products/15l-waterproof-dry-bag-backpack"
  },
  {
    "name": "Evo 27\" Mast",
    "price": "$599.00",
    "link": "/products/waydoo-flyer-evo-27-mast"
  },
  {
    "name": "Evo 31\" Mast",
    "price": "$1,499.00",
    "link": "/products/waydoo-flyer-evo-31-mast"
  },
  {
    "name": "Evo 35\" Mast",
    "price": "$799.00",
    "link": "/products/waydoo-flyer-evo-35-mast"
  },
  {
    "name": "Tactical Backpack",
    "price": "$189.00",
    "link": "/products/tactical-backpack"
  },
  {
    "name": "Fireproof Safe Bag",
    "price": "$79.90",
    "link": "/products/fireproof-safe-bag"
  },
  {
    "name": "Board Bag",
    "price": "$149.00",
    "link": "/products/board-bag"
  },
  {
    "name": "Board Bag Pro",
    "price": "$169.00",
    "link": "/products/board-bag-pro"
  },
  {
    "name": "Flyer ONE Plus",
    "price": "$3,999.00",
    "link": "/products/flyer-one-plus"
  },
  {
    "name": "Flyer ONE",
    "price": "$3,499.00",
    "link": "/products/flyer-one"
  },
  {
    "name": "Wing Set",
    "price": "$899.00",
    "link": "/products/wing-set"
  },
  {
    "name": "Battery Charger",
    "price": "$299.00",
    "link": "/products/battery-charger"
  }
]
```

</td>
</tr>
</table>

## Features

- Automatically navigate to product listing pages
- Extract product information using AI-powered extraction
- Handle popups, cookie banners, and overlays automatically
- Support for multiple websites in batch
- Save results as JSON files with screenshots
- Normalize and validate product data
- Built-in CAPTCHA solving support

## Use Cases

- **Price Monitoring**: Track product prices across multiple e-commerce sites
- **Competitive Analysis**: Compare product offerings from different retailers
- **Product Aggregation**: Collect product information for comparison shopping
- **Market Research**: Analyze product catalogs and pricing strategies
- **Inventory Tracking**: Monitor product availability across sites

## Framework Integration Guides

This project is structured to support multiple agent frameworks. Please refer to the specific framework integration guide for detailed setup and usage instructions:

- [LangChain Integration Guide](./langchain/README.md) - Complete setup and usage instructions for LangChain framework

## Project Structure

This project follows a modular structure that separates core functionality from framework-specific integrations:

```
e-commerce-inspector/
├── README.md            # This documentation
├── common/              # Public core functionality
│   └── src/             # Framework-agnostic code
│       └── __init__.py  # Python package initializer
└── langchain/           # LangChain integration
    ├── README.md        # LangChain integration documentation
    ├── requirements.txt # Python dependencies
    ├── data/            # Output directory for inspection results
    └── src/             # LangChain-specific code
        ├── __init__.py                      # Python package initializer
        ├── inspector_tools.py               # Core inspection tools
        ├── e_commerce_inspector.py          # Main inspector agent implementation
        └── e_commerce_inspector_example.py  # Example usage script
```

### Common Module

The [common](./common/) directory is intended for all the core functionality that can be used across different agent frameworks.

### Framework Integration Modules

Framework-specific directories (like [langchain](./langchain/)) contain the integration code that implements e-commerce inspection functionality using specific agent frameworks.

## How It Works

1. **Session Creation**: Creates an AgentBay browser session with CAPTCHA solving enabled
2. **Navigation**: Navigates to the target e-commerce website
3. **Page Analysis**: Uses AI to identify and navigate to product listing pages
4. **Data Extraction**: Extracts product information using structured extraction with Pydantic schemas
5. **Data Validation**: Normalizes links and validates product data
6. **Result Storage**: Saves results as JSON files and captures screenshots for verification

## Technical Highlights

### AI-Powered Extraction

The agent uses AgentBay's `extract_async` method with Pydantic schemas to extract structured data:

```python
class ProductInfo(BaseModel):
    name: str = Field(..., description="Product name")
    price: Optional[str] = Field(None, description="Price text")
    link: str = Field(..., description="Relative path to product page")

class InspectionResult(BaseModel):
    products: List[ProductInfo] = Field(..., description="All products on the page")
```

### Automatic Navigation

The agent can automatically:
- Navigate to product listing pages (Shop, Store, Catalog, etc.)
- Close popups and cookie banners
- Retry extraction if the initial attempt fails
- Handle different page layouts and structures

### Data Normalization

- Converts relative URLs to absolute URLs
- Validates product data (name, price, link)
- Filters out invalid entries
- Ensures minimum quality standards

## Customization

You can customize the inspector behavior by:

1. **Modifying extraction instructions**: Update the instruction text in `inspector_tools.py`
2. **Adjusting validation rules**: Change the `is_valid_product` function
3. **Adding new sites**: Simply provide new URLs to inspect
4. **Customizing output format**: Modify the JSON serialization in `process_site`

## AgentBay SDK Features Used

- Session management with browser environments
- Browser initialization with custom screen size
- CAPTCHA solving capabilities
- AI-powered browser agent for navigation and extraction
- Structured data extraction with Pydantic schemas
- Screenshot capture for verification
- Async/await support for efficient execution

## Output Files

After running the inspector, you'll find the following files in the `./data/` directory:

- **`inspection_[domain].json`** - Structured product data (name, price, link)
- **`screenshot_[domain].png`** - Screenshot of the product listing page (viewport only, optimized for documentation)

## Prerequisites

Before using this cookbook, you need to:

1. Register an Alibaba Cloud account: [https://aliyun.com](https://aliyun.com)
2. Get APIKEY credentials: [AgentBay Console](https://agentbay.console.aliyun.com/service-management)
3. Get DashScope API key for LLM: [DashScope Console](https://bailian.console.aliyun.com/#/home)

## Contributing

If you'd like to contribute improvements or add support for new frameworks, please follow the established structure and submit a pull request.

