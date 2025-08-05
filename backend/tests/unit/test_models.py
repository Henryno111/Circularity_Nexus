"""
Unit tests for database models
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from circularity_nexus.models.user import User
from circularity_nexus.models.waste_submission import WasteSubmission, WasteType, SubmissionStatus
from circularity_nexus.models.waste_token import WasteToken
from circularity_nexus.models.carbon_token import CarbonToken
from circularity_nexus.models.transaction import Transaction, TransactionType
from circularity_nexus.models.smart_bin import SmartBin
from circularity_nexus.models.recycling_vault import RecyclingVault, VaultType, StakeStatus


@pytest.mark.unit
class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self):
        """Test creating a user instance"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            full_name="Test User",
            wallet_address="0x1234567890abcdef1234567890abcdef12345678"
        )
        
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.wallet_address == "0x1234567890abcdef1234567890abcdef12345678"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.total_waste_kg == 0
        assert user.total_tokens_earned == 0
        assert user.carbon_credits_earned == 0
    
    def test_user_repr(self):
        """Test user string representation"""
        user = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password_123",
            full_name="Test User"
        )
        
        expected = "<User(id=1, email='test@example.com', name='Test User')>"
        assert repr(user) == expected
    
    async def test_user_database_constraints(self, test_session):
        """Test user database constraints"""
        # Test unique email constraint
        user1 = User(
            email="unique@example.com",
            hashed_password="password1",
            full_name="User One"
        )
        user2 = User(
            email="unique@example.com",  # Same email
            hashed_password="password2",
            full_name="User Two"
        )
        
        test_session.add(user1)
        await test_session.commit()
        
        test_session.add(user2)
        with pytest.raises(IntegrityError):
            await test_session.commit()


@pytest.mark.unit
class TestWasteSubmissionModel:
    """Test cases for WasteSubmission model"""
    
    def test_waste_submission_creation(self):
        """Test creating a waste submission instance"""
        submission = WasteSubmission(
            user_id=1,
            waste_type=WasteType.PET,
            estimated_weight_kg=1.5,
            location_lat=-1.286389,
            location_lng=36.817223,
            description="Clear plastic bottle"
        )
        
        assert submission.user_id == 1
        assert submission.waste_type == WasteType.PET
        assert submission.estimated_weight_kg == 1.5
        assert submission.status == SubmissionStatus.PENDING
        assert submission.tokens_minted == 0
        assert submission.carbon_credits_generated == 0
    
    def test_waste_submission_repr(self):
        """Test waste submission string representation"""
        submission = WasteSubmission(
            id=1,
            user_id=1,
            waste_type=WasteType.ALUMINUM,
            estimated_weight_kg=0.5
        )
        
        expected = "<WasteSubmission(id=1, type='WasteType.ALUMINUM', weight=0.5kg)>"
        assert repr(submission) == expected
    
    def test_waste_type_enum_values(self):
        """Test WasteType enum values"""
        assert WasteType.PET == "PET"
        assert WasteType.ALUMINUM == "ALUMINUM"
        assert WasteType.GLASS == "GLASS"
        assert WasteType.PAPER == "PAPER"
        assert WasteType.EWASTE == "EWASTE"
    
    def test_submission_status_enum_values(self):
        """Test SubmissionStatus enum values"""
        assert SubmissionStatus.PENDING == "PENDING"
        assert SubmissionStatus.AI_PROCESSING == "AI_PROCESSING"
        assert SubmissionStatus.VALIDATED == "VALIDATED"
        assert SubmissionStatus.REJECTED == "REJECTED"
        assert SubmissionStatus.TOKENIZED == "TOKENIZED"


@pytest.mark.unit
class TestWasteTokenModel:
    """Test cases for WasteToken model"""
    
    def test_waste_token_creation(self):
        """Test creating a waste token instance"""
        token = WasteToken(
            user_id=1,
            token_type="PET",
            balance=2500,  # 2.5kg in grams
            hedera_token_id="0.0.123456"
        )
        
        assert token.user_id == 1
        assert token.token_type == "PET"
        assert token.balance == 2500
        assert token.hedera_token_id == "0.0.123456"


@pytest.mark.unit
class TestCarbonTokenModel:
    """Test cases for CarbonToken model"""
    
    def test_carbon_token_creation(self):
        """Test creating a carbon token instance"""
        token = CarbonToken(
            user_id=1,
            balance=3.75,  # 3.75 kg CO2e
            hedera_token_id="0.0.789012"
        )
        
        assert token.user_id == 1
        assert token.balance == 3.75
        assert token.hedera_token_id == "0.0.789012"


@pytest.mark.unit
class TestTransactionModel:
    """Test cases for Transaction model"""
    
    def test_transaction_creation(self):
        """Test creating a transaction instance"""
        transaction = Transaction(
            user_id=1,
            transaction_type=TransactionType.MINT,
            token_type="PET",
            amount=1000.0,
            hedera_transaction_id="0.0.123456@1234567890.123456789"
        )
        
        assert transaction.user_id == 1
        assert transaction.transaction_type == TransactionType.MINT
        assert transaction.token_type == "PET"
        assert transaction.amount == 1000.0
        assert transaction.status == "PENDING"
    
    def test_transaction_type_enum_values(self):
        """Test TransactionType enum values"""
        assert TransactionType.MINT == "MINT"
        assert TransactionType.TRANSFER == "TRANSFER"
        assert TransactionType.STAKE == "STAKE"
        assert TransactionType.UNSTAKE == "UNSTAKE"
        assert TransactionType.CONVERT == "CONVERT"


@pytest.mark.unit
class TestSmartBinModel:
    """Test cases for SmartBin model"""
    
    def test_smart_bin_creation(self):
        """Test creating a smart bin instance"""
        bin = SmartBin(
            bin_id="NBO-001",
            location_lat=-1.286389,
            location_lng=36.817223,
            address="Nairobi, Kenya",
            capacity_kg=50.0,
            current_weight_kg=15.5
        )
        
        assert bin.bin_id == "NBO-001"
        assert bin.location_lat == -1.286389
        assert bin.location_lng == 36.817223
        assert bin.capacity_kg == 50.0
        assert bin.current_weight_kg == 15.5
        assert bin.battery_level == 100
        assert bin.is_active is True
    
    def test_smart_bin_fill_percentage(self):
        """Test calculating fill percentage"""
        bin = SmartBin(
            bin_id="TEST-001",
            location_lat=0.0,
            location_lng=0.0,
            capacity_kg=50.0,
            current_weight_kg=17.5
        )
        
        # Calculate fill percentage
        fill_percentage = (bin.current_weight_kg / bin.capacity_kg) * 100
        assert fill_percentage == 35.0


@pytest.mark.unit
class TestRecyclingVaultModel:
    """Test cases for RecyclingVault model"""
    
    def test_recycling_vault_creation(self):
        """Test creating a recycling vault instance"""
        vault = RecyclingVault(
            user_id=1,
            vault_type=VaultType.ESG_CORPORATE,
            token_type="PET",
            staked_amount=5000,  # 5kg in grams
            apy_rate=5.2
        )
        
        assert vault.user_id == 1
        assert vault.vault_type == VaultType.ESG_CORPORATE
        assert vault.token_type == "PET"
        assert vault.staked_amount == 5000
        assert vault.apy_rate == 5.2
        assert vault.rewards_earned == 0.0
        assert vault.status == StakeStatus.ACTIVE
    
    def test_vault_type_enum_values(self):
        """Test VaultType enum values"""
        assert VaultType.ESG_CORPORATE == "ESG_CORPORATE"
        assert VaultType.RECYCLING_POOL == "RECYCLING_POOL"
        assert VaultType.CARBON_OFFSET == "CARBON_OFFSET"
        assert VaultType.COMMUNITY == "COMMUNITY"
    
    def test_stake_status_enum_values(self):
        """Test StakeStatus enum values"""
        assert StakeStatus.ACTIVE == "ACTIVE"
        assert StakeStatus.UNSTAKING == "UNSTAKING"
        assert StakeStatus.COMPLETED == "COMPLETED"


@pytest.mark.unit
class TestModelRelationships:
    """Test model relationships and foreign keys"""
    
    async def test_user_waste_submissions_relationship(self, test_session):
        """Test user to waste submissions relationship"""
        # Create user
        user = User(
            email="test@example.com",
            hashed_password="password",
            full_name="Test User"
        )
        test_session.add(user)
        await test_session.flush()  # Get user ID
        
        # Create waste submission
        submission = WasteSubmission(
            user_id=user.id,
            waste_type=WasteType.PET,
            estimated_weight_kg=1.0
        )
        test_session.add(submission)
        await test_session.commit()
        
        # Test relationship
        assert submission.user_id == user.id
    
    def test_model_timestamps(self):
        """Test model timestamp fields"""
        user = User(
            email="test@example.com",
            hashed_password="password",
            full_name="Test User"
        )
        
        # created_at should be set automatically
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')
    
    def test_model_table_names(self):
        """Test model table names"""
        assert User.__tablename__ == "users"
        assert WasteSubmission.__tablename__ == "waste_submissions"
        assert WasteToken.__tablename__ == "waste_tokens"
        assert CarbonToken.__tablename__ == "carbon_tokens"
        assert Transaction.__tablename__ == "transactions"
        assert SmartBin.__tablename__ == "smart_bins"
        assert RecyclingVault.__tablename__ == "recycling_vaults"
