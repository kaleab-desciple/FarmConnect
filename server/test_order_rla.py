import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session, Query

# Add current dir to path
sys.path.append(os.getcwd())

from app.infrastructure.repositories.order_repo import OrderRepository
from app.core.auth import TokenPayload
from app.infrastructure.db.models import OrderORM, UserORM

class TestOrderRLA:
    @pytest.fixture
    def mock_session(self):
        session = MagicMock(spec=Session)
        query = MagicMock(spec=Query)
        
        # Setup the chain to always return the query mock
        query.filter.return_value = query
        query.join.return_value = query
        query.options.return_value = query
        query.one_or_none.return_value = None
        query.all.return_value = []
        
        session.query.return_value = query
        return session, query

    @pytest.fixture
    def repo(self, mock_session):
        session, _ = mock_session
        return OrderRepository(session)

    def test_admin_sees_all(self, repo, mock_session):
        session, query = mock_session
        token = TokenPayload({
            "sub": "admin-id",
            "realm_access": {"roles": ["ADMIN"]},
            "azp": "backend"
        })
        
        repo.list_all(current_user=token)
        
        # Check that no restrictive filters were applied
        for call in query.filter.call_args_list:
            arg = str(call[0][0])
            # The only expected filters should be on ID if get_by_id was called,
            # but here list_all shouldn't have any filters if admin.
            assert "farmer_id" not in arg
            assert "merchant_id" not in arg

    def test_farmer_restricted_to_own_orders(self, repo, mock_session):
        session, query = mock_session
        keycloak_id = "uuid-farmer"
        business_id = "FAR-00001"
        token = TokenPayload({
            "sub": keycloak_id,
            "realm_access": {"roles": ["FARMER"]},
            "azp": "backend"
        })
        
        # Mock bridging lookup
        farmer_orm = MagicMock()
        farmer_orm.id = business_id
        farmer_orm.keycloak_id = keycloak_id
        
        def side_effect(model):
            if "UserORM" in str(model):
                u_query = MagicMock(spec=Query)
                u_query.filter.return_value = u_query
                u_query.one_or_none.return_value = farmer_orm
                return u_query
            return query
        session.query.side_effect = side_effect
        
        repo.list_all(current_user=token)
        
        # Just check if 'farmer_id' column is in any filter string
        found_farmer_filter = any("farmer_id" in str(c[0][0]) for c in query.filter.call_args_list)
        assert found_farmer_filter

    def test_merchant_restricted_to_own_orders(self, repo, mock_session):
        session, query = mock_session
        keycloak_id = "uuid-merchant"
        business_id = "MER-00001"
        token = TokenPayload({
            "sub": keycloak_id,
            "realm_access": {"roles": ["MERCHANT"]},
            "azp": "backend"
        })
        
        # Mock bridging lookup
        merchant_orm = MagicMock()
        merchant_orm.id = business_id
        merchant_orm.keycloak_id = keycloak_id
        
        def side_effect(model):
            if "UserORM" in str(model):
                u_query = MagicMock(spec=Query)
                u_query.filter.return_value = u_query
                u_query.one_or_none.return_value = merchant_orm
                return u_query
            return query
        session.query.side_effect = side_effect
        
        repo.list_all(current_user=token)
        
        found_merchant_filter = any("merchant_id" in str(c[0][0]) for c in query.filter.call_args_list)
        assert found_merchant_filter

    def test_agent_restricted_by_region(self, repo, mock_session):
        session, query = mock_session
        keycloak_id = "uuid-agent"
        business_id = "AGE-00001"
        region = "Addis"
        token = TokenPayload({
            "sub": keycloak_id,
            "realm_access": {"roles": ["AGENT"]},
            "azp": "backend"
        })
        
        # Mock agent user fetch
        agent_orm = MagicMock()
        agent_orm.id = business_id
        agent_orm.keycloak_id = keycloak_id
        agent_orm.metadata_ = {"location": region}
        
        def side_effect(model):
            if "UserORM" in str(model):
                u_query = MagicMock(spec=Query)
                u_query.filter.return_value = u_query
                u_query.one_or_none.return_value = agent_orm
                return u_query
            return query
            
        session.query.side_effect = side_effect
        
        repo.list_all(current_user=token)
        
        # Verify join was called
        assert query.join.called
        
        # Verify region filter was applied (metadata is in User table)
        found_region_filter = any("metadata" in str(c[0][0]) or "location" in str(c[0][0]) for c in query.filter.call_args_list)
        assert found_region_filter
