"""
E-commerce inspector tools for LangChain integration.
Provides tools for extracting product information from e-commerce websites.
"""

import os
import json
import base64
import time
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse, urljoin
from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    """Product information model."""
    name: str = Field(..., description="Product name")
    price: Optional[str] = Field(None, description="Price text; can be empty")
    link: str = Field(..., description="Relative path to product page (e.g., /products/item1)")


class InspectionResult(BaseModel):
    """Inspection result containing all products on the page."""
    products: List[ProductInfo] = Field(..., description="All products on the page")


def domain_of(url: str) -> str:
    """Extract domain from URL."""
    return urlparse(url).netloc


def normalize_abs_link(base_url: str, link: str) -> Optional[str]:
    """Normalize relative links to absolute URLs."""
    link = (link or "").strip()
    if not link or link.startswith("#"):
        return None
    if link.startswith("/"):
        return urljoin(base_url, link)
    return link


def normalize_links(base_url: str, products: List[ProductInfo]) -> List[ProductInfo]:
    """Normalize all product links to absolute URLs."""
    out: List[ProductInfo] = []
    for p in products:
        abs_link = normalize_abs_link(base_url, p.link)
        if not abs_link:
            continue
        out.append(
            ProductInfo(
                name=p.name.strip(), price=(p.price or "").strip(), link=abs_link
            )
        )
    return out


def is_valid_product(p: ProductInfo) -> bool:
    """Check if a product has valid information."""
    has_name = bool(p.name and p.name.strip())
    has_valid_link = bool(p.link and p.link.strip())
    has_price = bool(p.price and p.price.strip())

    return has_name and (has_valid_link or has_price)


def has_valid_products(products: List[ProductInfo], min_items: int = 2) -> bool:
    """Check if there are enough valid products."""
    goods = [p for p in products if is_valid_product(p)]
    return len(goods) >= min_items


def act(agent, instruction: str) -> bool:
    """Execute an action using the browser agent."""
    from agentbay import ActOptions

    print(f"Acting: {instruction}")
    ret = agent.act(ActOptions(action=instruction))
    return bool(getattr(ret, "success", False))


def take_and_save_screenshot(agent, base_url: str, out_dir: str, session=None, page=None) -> Optional[str]:
    """Take a screenshot and save it to the output directory."""
    try:
        host = urlparse(base_url).netloc
        
        # Take screenshot (viewport only, not full page)
        data_url = agent.screenshot(full_page=False, quality=90)
        
        if not isinstance(data_url, str):
            print(f"Screenshot failed for {base_url}: non-string response")
            return None
        
        if data_url.startswith("Screenshot failed:") or data_url.startswith("screenshot failed:"):
            print(f"Screenshot failed for {base_url}: {data_url[:100]}")
            return None
        
        # Extract base64 data from data URL
        if data_url.startswith("data:image/"):
            _, encoded = data_url.split(",", 1)
        else:
            encoded = data_url
        
        # Decode base64 to bytes
        try:
            image_data = base64.b64decode(encoded)
        except Exception as e:
            print(f"Failed to decode base64 for {base_url}: {e}")
            return None
        
        if not image_data:
            print(f"Decoded image is empty for {base_url}")
            return None
        
        # Save directly to local
        os.makedirs(out_dir, exist_ok=True)
        local_path = os.path.join(out_dir, f"screenshot_{host}.png")
        
        with open(local_path, "wb") as f:
            f.write(image_data)
        
        print(f"Screenshot for {base_url} saved to: {local_path}")
        return local_path
    except Exception as e:
        print(f"Failed to take screenshot for {base_url}: {e}")
        return None


def extract_products(agent, base_url: str) -> Optional[List[ProductInfo]]:
    """Extract products from the current page."""
    from agentbay import ExtractOptions

    ok, data = agent.extract(
        ExtractOptions(
            instruction=(
                "Please extract all products on this page. "
                "Price can be a range (e.g., $199–$299) or 'from $199'. "
                "For product links, return only the relative path (e.g., /path/to/product), "
                "do not include the domain name."
            ),
            schema=InspectionResult,
            use_text_extract=True,
        )
    )
    if not ok or not isinstance(data, InspectionResult) or not data.products:
        return None

    products = normalize_links(base_url, data.products)
    if not has_valid_products(products):
        print(
            f"Extracted products from {base_url} but none were valid after normalization."
        )
        return None

    return products


def ensure_listing_page(
    agent, base_url: str, out_dir: str, max_steps: int = 3
) -> List[ProductInfo]:
    """Ensure we are on a product listing page and extract products."""
    common_action = (
        "Navigate to the product listing page, such as 'Shop', 'Store', 'All products', "
        "'Catalog', or 'Collections' pages. If the current page is not a product listing page, "
        "please go to the product listing or catalog page (list or grid view). "
        "If there are popups, cookie banners, or overlays, please close them first."
    )
    act(agent, common_action)
    time.sleep(0.6)

    for i in range(max_steps):
        print(f"Extraction attempt {i+1}/{max_steps} for {base_url}...")
        products_found = extract_products(agent, base_url)
        if products_found is not None:
            valid_count = len([p for p in products_found if is_valid_product(p)])
            print(
                f"Extraction successful on attempt {i+1}. Found {valid_count} valid products."
            )

            take_and_save_screenshot(agent, base_url, out_dir)
            return products_found

        if i < max_steps - 1:
            print("Extraction failed, attempting to navigate to a listing page...")
            act(agent, common_action)
            time.sleep(0.6)

    print(f"All {max_steps} extraction attempts failed for {base_url}.")
    return []


def process_site(
    agent, url: str, out_dir: str = "./data", captcha_wait_time: int = 40
) -> dict:
    """Process a single e-commerce site and extract product information."""
    host = domain_of(url)
    agent.navigate(url)

    # Check if CAPTCHA is detected (can be customized based on specific sites)
    # For now, we'll skip CAPTCHA detection
    # If needed, add CAPTCHA detection logic here

    products_from_page = ensure_listing_page(agent, url, out_dir, max_steps=3)
    products = [p for p in products_from_page if is_valid_product(p)]

    out_path = os.path.join(out_dir, f"inspection_{host}.json")
    os.makedirs(out_dir, exist_ok=True)

    result = {
        "url": url,
        "host": host,
        "product_count": len(products),
        "output_file": out_path if products else None,
        "success": len(products) > 0
    }

    if products:
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(
                    [p.model_dump(mode="json") for p in products],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            priced_cnt = sum(1 for p in products if p.price)
            print(
                f"{host} -> {len(products)} items (with price: {priced_cnt}) saved: {out_path}"
            )
        except Exception as e:
            print(f"{host} -> save failed: {e}")
            result["success"] = False
            result["error"] = str(e)
    else:
        print(f"{host} -> no products found (name+link/price)")

    return result

