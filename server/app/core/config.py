import os

class Settings:
    PROJECT_NAME: str = "Farmer-Merchant Connector"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost/agri_db")
    
    # Keycloak Configuration
    KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
    KEYCLOAK_REALM: str = os.getenv("KEYCLOAK_REALM", "farm-connect")
    KEYCLOAK_CLIENT_ID: str = os.getenv("KEYCLOAK_CLIENT_ID", "farm-connect-backend")
    KEYCLOAK_CLIENT_SECRET: str = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    
    # Admin API credentials (for user provisioning)
    KEYCLOAK_ADMIN_USER: str = os.getenv("KEYCLOAK_ADMIN_USER", "admin")
    KEYCLOAK_ADMIN_PASSWORD: str = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")
    
    # JWT Configuration
    @property
    def KEYCLOAK_JWKS_URL(self) -> str:
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    
    @property
    def KEYCLOAK_ISSUER(self) -> str:
        # Allow overriding the issuer URL for validation
        # This is useful when running in Docker where internal URL (keycloak:8080)
        # differs from public URL (localhost:8080) in the token
        issuer_url = os.getenv("KEYCLOAK_ISSUER_URL")
        if issuer_url:
            return issuer_url
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}"
    
    @property
    def KEYCLOAK_TOKEN_URL(self) -> str:
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/token"
    
    KEYCLOAK_AUDIENCE: str = "account"  # Default Keycloak audience
    
    # Authentication settings
    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "true").lower() == "true"

settings = Settings()