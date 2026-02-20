from __future__ import annotations
from sqlalchemy.orm import Session
from typing import Optional
from shared_models import (
    Product as ProductDTO,
    ProductCreate,
    ProductUpdate
)
from app.domain.products.entities import Product as DomainProduct
from app.infrastructure.repositories.user_repo import UserRepository
from app.infrastructure.repositories.product_repo import ProductRepository


class ProductService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.product_repo = ProductRepository(session)

    def create_product(self, product_data: ProductCreate) -> ProductDTO:
        # Validate business rules
        if not product_data.name or not product_data.farmer_id:
            raise ValueError("Product name and farmer_id are required")

        # Check if farmer exists
        farmer = self.user_repo.get_by_id(product_data.farmer_id)
        if not farmer:
            raise ValueError("Farmer not found")

        # Create domain product
        domain_product = DomainProduct(
            farmer_id=product_data.farmer_id,
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            unit=product_data.unit,
            base_price=product_data.base_price,
            currency=product_data.currency,
            total_quantity=product_data.quantity_available if hasattr(product_data, 'quantity_available') else 0,
            quality_grade=product_data.quality_grade,
            harvest_date=product_data.harvest_date,
            expiry_date=product_data.expiry_date,
            location=product_data.location,
            images=product_data.images,
            is_active=product_data.is_active,
            metadata=product_data.metadata
        )

        # Save product
        saved_product = self.product_repo.save(domain_product)

        # Convert to DTO
        from app.infrastructure.db.mappers import domain_to_dto
        product_dto = domain_to_dto(saved_product)

        # Commit transaction
        self.session.commit()

        return product_dto

    def get_product_by_id(self, product_id: str) -> Optional[ProductDTO]:
        # Get domain product
        domain_product = self.product_repo.get_by_id(product_id)
        
        if not domain_product:
            return None

        # Convert to DTO
        from app.infrastructure.db.mappers import domain_to_dto
        product_dto = domain_to_dto(domain_product)

        return product_dto
    
    def get_products_by_farmer_id(self, farmer_id: str) -> list[ProductDTO]:
        # Get domain products
        domain_products = self.product_repo.get_by_farmer_id(farmer_id)

        # Convert to DTO
        from app.infrastructure.db.mappers import domain_to_dto
        product_dtos = [domain_to_dto(domain_product) for domain_product in domain_products]

        return product_dtos
    
    def get_active_products(self) -> list[ProductDTO]:
        # Get domain products
        domain_products = self.product_repo.list_active()

        # Convert to  DTO
        from app.infrastructure.db.mappers import domain_to_dto
        product_dtos = [domain_to_dto(domain_product) for domain_product in domain_products]

        return product_dtos
    
    def get_all_products(self) -> list[ProductDTO]:
        # Get domain products
        domain_products = self.product_repo.list_all()

        # Convert to DTO
        from app.infrastructure.db.mappers import domain_to_dto
        product_dtos = [domain_to_dto(domain_product) for domain_product in domain_products]

        return product_dtos

    def update_product(self, product_id: str, product_data: ProductUpdate) -> Optional[ProductDTO]:
        domain_product = self.product_repo.get_by_id(product_id)
        if not domain_product:
            return None

        update_dict = product_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(domain_product, key, value)
        
        # update updated_at if it exists on domain model
        # domain_product.updated_at = datetime.now(...) # Assuming domain has this or repo handles it
        
        saved_product = self.product_repo.save(domain_product)
        self.session.commit()
        
        from app.infrastructure.db.mappers import domain_to_dto
        return domain_to_dto(saved_product)
    