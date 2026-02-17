from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from shared_models import Product as ProductDTO, ProductCreate
from app.core.database import get_db
from app.core.auth import require_permission
from .service import ProductService

router = APIRouter()

@router.post("/", response_model=ProductDTO, dependencies=[Depends(require_permission("products:create"))])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product listing.
    
    Farmers create product listings to make their harvest available for sale
    in the marketplace. Each product includes details like category, quantity,
    pricing, and quality information.
    
    ## Request Body
    - **farmer_id**: UUID of the farmer listing the product (required)
    - **category**: Product category (VEGETABLES, FRUITS, GRAINS, etc.) (required)
    - **name**: Product name (required)
    - **description**: Product description (optional)
    - **quantity_kg**: Available quantity in kilograms (required)
    - **unit_price_usd**: Price per kg in USD (required)
    - **quality_grade**: Quality grade (A, B, C) (optional)
    - **organic_certified**: Organic certification status (optional)
    - **harvest_date**: When harvested (optional)
    - **available_from**: Availability start date (optional)
    - **location**: Pickup location (optional)
    
    ## Authentication & Authorization
    Requires `products:create` permission.
    Farmers can only create products for themselves.
    
    ## Validation
    - Quantity must be positive
    - Unit price must be positive
    - Category must be valid enum value
    - Farmer must exist in the system
    
    ## Responses
    - **200**: Product created successfully
    - **400**: Invalid product data or validation error
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing products:create permission)
    - **500**: Internal server error
    """
    service = ProductService(db)
    try:
        return service.create_product(product)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise e


@router.get("/", response_model=List[ProductDTO], dependencies=[Depends(require_permission("products:read"))])
def get_all_products(db: Session=Depends(get_db)):
    """
    List all available products in the marketplace.
    
    Retrieves all product listings from all farmers that are currently
    available for purchase. Used to populate the marketplace catalog.
    
    ## Authentication & Authorization
    Requires `products:read` permission.
    Available to all authenticated users (farmers, merchants, agents).
    
    ## Response
    Returns array of all product listings with complete details including:
    - Product information (name, category, description)
    - Pricing and availability
    - Farmer information
    - Quality and certification details
    - Stock levels
    
    ## Use Cases
    - Marketplace product browsing
    - Product search and filtering
    - Inventory overview
    - Price comparison
    
    ## Responses
    - **200**: Products retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing products:read permission)
    - **500**: Internal server error
    """
    service = ProductService(db)
    return service.get_all_products()

@router.get("/farmer/{farmer_id}", response_model=List[ProductDTO], dependencies=[Depends(require_permission("products:read"))])
def get_products_by_farmer_id(farmer_id: str, db: Session = Depends(get_db)):
    """
    Get all products listed by a specific farmer.
    
    Retrieves all product listings belonging to a particular farmer.
    Useful for viewing a farmer's complete inventory and offerings.
    
    ## Path Parameters
    - **farmer_id**: UUID of the farmer (required)
    
    ## Authentication & Authorization
    Requires `products:read` permission.
    
    ## Response
    Returns array of product listings for the specified farmer.
    Empty array if farmer has no products listed.
    
    ## Use Cases
    - Farmer inventory management
    - Farmer profile product showcase
    - Tracking farmer's available products
    - Agricultural agent monitoring
    
    ## Responses
    - **200**: Products retrieved successfully (may be empty array)
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing products:read permission)
    - **404**: Farmer not found or has no products
    - **500**: Internal server error
    """
    service = ProductService(db)
    farmer_product = service.get_products_by_farmer_id(farmer_id)
    if not farmer_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return farmer_product 
@router.get("/{product_id}", response_model=ProductDTO, dependencies=[Depends(require_permission("products:read"))])
def get_product_by_id(product_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific product.
    
    Retrieves complete details for a single product listing including
    all metadata, pricing, availability, and farmer information.
    
    ## Path Parameters
    - **product_id**: UUID of the product (required)
    
    ## Authentication & Authorization
    Requires `products:read` permission.
    
    ## Response
    Returns complete product details:
    - Product identification (id, name, category)
    - Pricing (unit_price_usd, total value)
    - Quantity (quantity_kg, available stock)
    - Quality (quality_grade, organic_certified)
    - Dates (harvest_date, available_from, created_at)
    - Farmer information (farmer_id)
    - Location and logistics details
    
    ## Use Cases
    - Product detail page
    - Order creation (verify availability and pricing)
    - Product comparison
    - Inventory tracking
    
    ## Responses
    - **200**: Product details retrieved successfully
    - **401**: Unauthorized (not authenticated)
    - **403**: Forbidden (missing products:read permission)
    - **404**: Product not found
    - **500**: Internal server error
    """
    service = ProductService(db)
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product 
