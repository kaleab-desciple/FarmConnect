from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared_models import Product as ProductDTO
from app.core.database import get_db
from app.core.auth import require_permission
from .service import ProductService

router = APIRouter()

@router.post("/", response_model=ProductDTO, dependencies=[Depends(require_permission("products:create"))])
def create_product(product: ProductDTO, db: Session = Depends(get_db)):
    service = ProductService(db)
    try:
        return service.create_product(product)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise e
