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
    service = ProductService(db)
    return service.get_all_products()

@router.get("/farmer/{farmer_id}", response_model=List[ProductDTO], dependencies=[Depends(require_permission("products:read"))])
def get_products_by_farmer_id(farmer_id: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    farmer_product = service.get_products_by_farmer_id(farmer_id)
    if not farmer_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return farmer_product 
@router.get("/{product_id}", response_model=ProductDTO, dependencies=[Depends(require_permission("products:read"))])
def get_product_by_id(product_id: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    product = service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product 
