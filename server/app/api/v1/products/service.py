from sqlalchemy.orm import Session
from shared_models import Product as ProductDTO
from app.domain.products.entities import Product as DomainProduct
from app.infrastructure.repositories.user_repo import UserRepository
from app.infrastructure.repositories.product_repo import ProductRepository


class ProductService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.product_repo = ProductRepository(session)

    def create_product(self, product_data: ProductDTO) -> ProductDTO:
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
            quantity_available=product_data.quantity_available,
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
