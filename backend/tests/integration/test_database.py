"""
Integration tests for database operations
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from circularity_nexus.models.user import User
from circularity_nexus.models.waste_submission import WasteSubmission, WasteType, SubmissionStatus
from circularity_nexus.models.waste_token import WasteToken
from circularity_nexus.models.carbon_token import CarbonToken
from circularity_nexus.models.transaction import Transaction, TransactionType
from circularity_nexus.models.smart_bin import SmartBin
from circularity_nexus.models.recycling_vault import RecyclingVault, VaultType, StakeStatus


@pytest.mark.integration
class TestDatabaseOperations:
    """Test database CRUD operations"""
    
    async def test_create_user(self, test_session):
        """Test creating a user in database"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            full_name="Test User",
            wallet_address="0x1234567890abcdef1234567890abcdef12345678"
        )
        
        test_session.add(user)
        await test_session.commit()
        
        # Verify user was created
        result = await test_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        created_user = result.scalar_one()
        
        assert created_user.email == "test@example.com"
        assert created_user.full_name == "Test User"
        assert created_user.is_active is True
        assert created_user.created_at is not None
    
    async def test_create_waste_submission(self, test_session):
        """Test creating a waste submission in database"""
        # First create a user
        user = User(
            email="submitter@example.com",
            hashed_password="password",
            full_name="Submitter"
        )
        test_session.add(user)
        await test_session.flush()
        
        # Create waste submission
        submission = WasteSubmission(
            user_id=user.id,
            waste_type=WasteType.PET,
            estimated_weight_kg=1.5,
            location_lat=-1.286389,
            location_lng=36.817223,
            description="Clear plastic bottle"
        )
        
        test_session.add(submission)
        await test_session.commit()
        
        # Verify submission was created
        result = await test_session.execute(
            select(WasteSubmission).where(WasteSubmission.user_id == user.id)
        )
        created_submission = result.scalar_one()
        
        assert created_submission.waste_type == WasteType.PET
        assert created_submission.estimated_weight_kg == 1.5
        assert created_submission.status == SubmissionStatus.PENDING
        assert created_submission.created_at is not None
    
    async def test_create_waste_token(self, test_session):
        """Test creating a waste token in database"""
        # Create user first
        user = User(
            email="token_holder@example.com",
            hashed_password="password",
            full_name="Token Holder"
        )
        test_session.add(user)
        await test_session.flush()
        
        # Create waste token
        token = WasteToken(
            user_id=user.id,
            token_type="PET",
            balance=2500,
            hedera_token_id="0.0.123456"
        )
        
        test_session.add(token)
        await test_session.commit()
        
        # Verify token was created
        result = await test_session.execute(
            select(WasteToken).where(WasteToken.user_id == user.id)
        )
        created_token = result.scalar_one()
        
        assert created_token.token_type == "PET"
        assert created_token.balance == 2500
        assert created_token.hedera_token_id == "0.0.123456"
    
    async def test_create_carbon_token(self, test_session):
        """Test creating a carbon token in database"""
        # Create user first
        user = User(
            email="carbon_holder@example.com",
            hashed_password="password",
            full_name="Carbon Holder"
        )
        test_session.add(user)
        await test_session.flush()
        
        # Create carbon token
        token = CarbonToken(
            user_id=user.id,
            balance=3.75,
            hedera_token_id="0.0.789012"
        )
        
        test_session.add(token)
        await test_session.commit()
        
        # Verify token was created
        result = await test_session.execute(
            select(CarbonToken).where(CarbonToken.user_id == user.id)
        )
        created_token = result.scalar_one()
        
        assert created_token.balance == 3.75
        assert created_token.hedera_token_id == "0.0.789012"
    
    async def test_create_transaction(self, test_session):
        """Test creating a transaction in database"""
        # Create user first
        user = User(
            email="transactor@example.com",
            hashed_password="password",
            full_name="Transactor"
        )
        test_session.add(user)
        await test_session.flush()
        
        # Create transaction
        transaction = Transaction(
            user_id=user.id,
            transaction_type=TransactionType.MINT,
            token_type="PET",
            amount=1000.0,
            hedera_transaction_id="0.0.123456@1234567890.123456789"
        )
        
        test_session.add(transaction)
        await test_session.commit()
        
        # Verify transaction was created
        result = await test_session.execute(
            select(Transaction).where(Transaction.user_id == user.id)
        )
        created_transaction = result.scalar_one()
        
        assert created_transaction.transaction_type == TransactionType.MINT
        assert created_transaction.token_type == "PET"
        assert created_transaction.amount == 1000.0
        assert created_transaction.status == "PENDING"
    
    async def test_create_smart_bin(self, test_session):
        """Test creating a smart bin in database"""
        bin = SmartBin(
            bin_id="TEST-BIN-001",
            location_lat=-1.286389,
            location_lng=36.817223,
            address="Test Location",
            capacity_kg=50.0,
            current_weight_kg=15.5
        )
        
        test_session.add(bin)
        await test_session.commit()
        
        # Verify bin was created
        result = await test_session.execute(
            select(SmartBin).where(SmartBin.bin_id == "TEST-BIN-001")
        )
        created_bin = result.scalar_one()
        
        assert created_bin.location_lat == -1.286389
        assert created_bin.location_lng == 36.817223
        assert created_bin.capacity_kg == 50.0
        assert created_bin.current_weight_kg == 15.5
        assert created_bin.is_active is True
    
    async def test_create_recycling_vault(self, test_session):
        """Test creating a recycling vault in database"""
        # Create user first
        user = User(
            email="staker@example.com",
            hashed_password="password",
            full_name="Staker"
        )
        test_session.add(user)
        await test_session.flush()
        
        # Create recycling vault
        vault = RecyclingVault(
            user_id=user.id,
            vault_type=VaultType.ESG_CORPORATE,
            token_type="PET",
            staked_amount=5000,
            apy_rate=5.2
        )
        
        test_session.add(vault)
        await test_session.commit()
        
        # Verify vault was created
        result = await test_session.execute(
            select(RecyclingVault).where(RecyclingVault.user_id == user.id)
        )
        created_vault = result.scalar_one()
        
        assert created_vault.vault_type == VaultType.ESG_CORPORATE
        assert created_vault.token_type == "PET"
        assert created_vault.staked_amount == 5000
        assert created_vault.apy_rate == 5.2
        assert created_vault.status == StakeStatus.ACTIVE


@pytest.mark.integration
class TestDatabaseConstraints:
    """Test database constraints and validations"""
    
    async def test_user_email_unique_constraint(self, test_session):
        """Test user email uniqueness constraint"""
        # Create first user
        user1 = User(
            email="unique@example.com",
            hashed_password="password1",
            full_name="User One"
        )
        test_session.add(user1)
        await test_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="unique@example.com",
            hashed_password="password2",
            full_name="User Two"
        )
        test_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()
    
    async def test_smart_bin_id_unique_constraint(self, test_session):
        """Test smart bin ID uniqueness constraint"""
        # Create first bin
        bin1 = SmartBin(
            bin_id="UNIQUE-BIN-001",
            location_lat=0.0,
            location_lng=0.0
        )
        test_session.add(bin1)
        await test_session.commit()
        
        # Try to create second bin with same ID
        bin2 = SmartBin(
            bin_id="UNIQUE-BIN-001",
            location_lat=1.0,
            location_lng=1.0
        )
        test_session.add(bin2)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()
    
    async def test_foreign_key_constraints(self, test_session):
        """Test foreign key constraints"""
        # Try to create waste submission without valid user
        submission = WasteSubmission(
            user_id=99999,  # Non-existent user ID
            waste_type=WasteType.PET,
            estimated_weight_kg=1.0
        )
        test_session.add(submission)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()


@pytest.mark.integration
class TestDatabaseQueries:
    """Test complex database queries"""
    
    async def test_user_with_submissions_query(self, test_session):
        """Test querying user with their submissions"""
        # Create user
        user = User(
            email="query_test@example.com",
            hashed_password="password",
            full_name="Query Test User"
        )
        test_session.add(user)
        await test_session.flush()
        
        # Create multiple submissions
        submissions = [
            WasteSubmission(
                user_id=user.id,
                waste_type=WasteType.PET,
                estimated_weight_kg=1.0
            ),
            WasteSubmission(
                user_id=user.id,
                waste_type=WasteType.ALUMINUM,
                estimated_weight_kg=0.5
            )
        ]
        
        for submission in submissions:
            test_session.add(submission)
        await test_session.commit()
        
        # Query user submissions
        result = await test_session.execute(
            select(WasteSubmission).where(WasteSubmission.user_id == user.id)
        )
        user_submissions = result.scalars().all()
        
        assert len(user_submissions) == 2
        assert user_submissions[0].waste_type == WasteType.PET
        assert user_submissions[1].waste_type == WasteType.ALUMINUM
    
    async def test_token_balance_aggregation(self, test_session):
        """Test aggregating token balances"""
        # Create user
        user = User(
            email="balance_test@example.com",
            hashed_password="password",
            full_name="Balance Test User"
        )
        test_session.add(user)
        await test_session.flush()
        
        # Create multiple tokens
        tokens = [
            WasteToken(
                user_id=user.id,
                token_type="PET",
                balance=1000,
                hedera_token_id="0.0.111111"
            ),
            WasteToken(
                user_id=user.id,
                token_type="ALUMINUM",
                balance=500,
                hedera_token_id="0.0.222222"
            )
        ]
        
        for token in tokens:
            test_session.add(token)
        await test_session.commit()
        
        # Query user tokens
        result = await test_session.execute(
            select(WasteToken).where(WasteToken.user_id == user.id)
        )
        user_tokens = result.scalars().all()
        
        total_balance = sum(token.balance for token in user_tokens)
        assert total_balance == 1500
    
    async def test_transaction_history_query(self, test_session):
        """Test querying transaction history"""
        # Create user
        user = User(
            email="transaction_test@example.com",
            hashed_password="password",
            full_name="Transaction Test User"
        )
        test_session.add(user)
        await test_session.flush()
        
        # Create transactions
        transactions = [
            Transaction(
                user_id=user.id,
                transaction_type=TransactionType.MINT,
                token_type="PET",
                amount=1000.0,
                hedera_transaction_id="0.0.123456@1111111111.111111111"
            ),
            Transaction(
                user_id=user.id,
                transaction_type=TransactionType.STAKE,
                token_type="PET",
                amount=500.0,
                hedera_transaction_id="0.0.123456@2222222222.222222222"
            )
        ]
        
        for transaction in transactions:
            test_session.add(transaction)
        await test_session.commit()
        
        # Query user transactions
        result = await test_session.execute(
            select(Transaction)
            .where(Transaction.user_id == user.id)
            .order_by(Transaction.created_at.desc())
        )
        user_transactions = result.scalars().all()
        
        assert len(user_transactions) == 2
        assert user_transactions[0].transaction_type == TransactionType.STAKE  # Most recent
        assert user_transactions[1].transaction_type == TransactionType.MINT


@pytest.mark.integration
class TestDatabasePerformance:
    """Test database performance and optimization"""
    
    async def test_bulk_insert_performance(self, test_session):
        """Test bulk insert performance"""
        import time
        
        # Create multiple users in bulk
        users = []
        for i in range(100):
            user = User(
                email=f"bulk_user_{i}@example.com",
                hashed_password=f"password_{i}",
                full_name=f"Bulk User {i}"
            )
            users.append(user)
        
        start_time = time.time()
        test_session.add_all(users)
        await test_session.commit()
        end_time = time.time()
        
        # Verify all users were created
        result = await test_session.execute(
            select(User).where(User.email.like("bulk_user_%"))
        )
        created_users = result.scalars().all()
        
        assert len(created_users) == 100
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
    
    async def test_index_performance(self, test_session):
        """Test database index performance"""
        import time
        
        # Create user and many submissions
        user = User(
            email="index_test@example.com",
            hashed_password="password",
            full_name="Index Test User"
        )
        test_session.add(user)
        await test_session.flush()
        
        # Create many submissions
        submissions = []
        for i in range(1000):
            submission = WasteSubmission(
                user_id=user.id,
                waste_type=WasteType.PET,
                estimated_weight_kg=1.0
            )
            submissions.append(submission)
        
        test_session.add_all(submissions)
        await test_session.commit()
        
        # Test query performance (should use index on user_id)
        start_time = time.time()
        result = await test_session.execute(
            select(WasteSubmission).where(WasteSubmission.user_id == user.id)
        )
        user_submissions = result.scalars().all()
        end_time = time.time()
        
        assert len(user_submissions) == 1000
        assert end_time - start_time < 1.0  # Should be fast with index
