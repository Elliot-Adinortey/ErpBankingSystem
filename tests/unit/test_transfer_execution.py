"""
Unit tests for transfer execution and tracking functionality
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from user import User
from account import Account
from transfer_manager import TransferManager, TransferTransaction


class TestTransferExecution(unittest.TestCase):
    """Test transfer execution functionality"""
    
    def setUp(self):
        """Set up test fixtures with real User and Account objects"""
        # Create a real user for integration testing
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create real accounts
        self.savings_account = Account("savings", 1000.0, 0, "My Savings")
        self.current_account = Account("current", 500.0, 200.0, "My Current")
        
        # Add accounts to user
        self.user.accounts = [self.savings_account, self.current_account]
        
        # Create transfer manager
        self.transfer_manager = TransferManager(self.user)
    
    def test_transfer_execution_balance_updates(self):
        """Test that transfer execution correctly updates account balances"""
        initial_savings_balance = self.savings_account.balance
        initial_current_balance = self.current_account.balance
        transfer_amount = 300.0
        
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "savings", "current", transfer_amount, "Test transfer"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(transfer_id)
        
        # Check balance updates
        self.assertEqual(self.savings_account.balance, initial_savings_balance - transfer_amount)
        self.assertEqual(self.current_account.balance, initial_current_balance + transfer_amount)
    
    def test_transfer_execution_transaction_creation(self):
        """Test that transfer execution creates proper transaction records"""
        transfer_amount = 150.0
        memo = "Transfer for bills"
        
        # Record initial transaction counts
        initial_savings_transactions = len(self.savings_account.transactions)
        initial_current_transactions = len(self.current_account.transactions)
        
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "savings", "current", transfer_amount, memo
        )
        
        self.assertTrue(success)
        
        # Check transaction creation
        self.assertEqual(len(self.savings_account.transactions), initial_savings_transactions + 1)
        self.assertEqual(len(self.current_account.transactions), initial_current_transactions + 1)
        
        # Check outgoing transaction (from savings)
        outgoing_transaction = self.savings_account.transactions[-1]
        self.assertIsInstance(outgoing_transaction, TransferTransaction)
        self.assertEqual(outgoing_transaction.amount, transfer_amount)
        self.assertEqual(outgoing_transaction.memo, memo)
        self.assertEqual(outgoing_transaction.transfer_id, transfer_id)
        self.assertTrue(outgoing_transaction.is_outgoing)
        self.assertEqual(outgoing_transaction.from_account, "savings")
        self.assertEqual(outgoing_transaction.to_account, "current")
        
        # Check incoming transaction (to current)
        incoming_transaction = self.current_account.transactions[-1]
        self.assertIsInstance(incoming_transaction, TransferTransaction)
        self.assertEqual(incoming_transaction.amount, transfer_amount)
        self.assertEqual(incoming_transaction.memo, memo)
        self.assertEqual(incoming_transaction.transfer_id, transfer_id)
        self.assertFalse(incoming_transaction.is_outgoing)
        self.assertEqual(incoming_transaction.from_account, "savings")
        self.assertEqual(incoming_transaction.to_account, "current")
    
    def test_transfer_id_generation_uniqueness(self):
        """Test that transfer IDs are unique for multiple transfers"""
        transfer_ids = set()
        
        # Execute multiple transfers
        for i in range(5):
            success, message, transfer_id = self.transfer_manager.execute_transfer(
                "current", "savings", 10.0, f"Transfer {i}"
            )
            self.assertTrue(success)
            self.assertIsNotNone(transfer_id)
            self.assertNotIn(transfer_id, transfer_ids)
            transfer_ids.add(transfer_id)
        
        # Verify all IDs are unique
        self.assertEqual(len(transfer_ids), 5)
    
    def test_transfer_id_format(self):
        """Test that transfer IDs follow the expected format"""
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "savings", "current", 50.0
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(transfer_id)
        self.assertTrue(transfer_id.startswith("TXF-"))
        self.assertEqual(len(transfer_id), 12)  # TXF- + 8 characters
    
    def test_transfer_with_overdraft(self):
        """Test transfer execution using overdraft facility"""
        # Transfer more than current account balance but within overdraft limit
        transfer_amount = 600.0  # Current balance is 500, overdraft is 200
        
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "current", "savings", transfer_amount
        )
        
        self.assertTrue(success)
        self.assertEqual(self.current_account.balance, -100.0)  # 500 - 600
        self.assertEqual(self.savings_account.balance, 1600.0)  # 1000 + 600
    
    def test_transfer_exceeding_overdraft(self):
        """Test transfer execution that exceeds overdraft limit"""
        # Try to transfer more than available balance + overdraft
        transfer_amount = 800.0  # Current balance (500) + overdraft (200) = 700 available
        
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "current", "savings", transfer_amount
        )
        
        self.assertFalse(success)
        self.assertIn("Insufficient funds", message)
        self.assertIsNone(transfer_id)
        
        # Verify no changes were made
        self.assertEqual(self.current_account.balance, 500.0)
        self.assertEqual(self.savings_account.balance, 1000.0)
    
    def test_transfer_by_nickname(self):
        """Test transfer execution using account nicknames"""
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "My Savings", "My Current", 200.0, "Transfer by nickname"
        )
        
        self.assertTrue(success)
        self.assertEqual(self.savings_account.balance, 800.0)
        self.assertEqual(self.current_account.balance, 700.0)
    
    def test_transfer_confirmation_message(self):
        """Test that transfer confirmation message contains correct information"""
        transfer_amount = 250.0
        
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "savings", "current", transfer_amount, "Test confirmation"
        )
        
        self.assertTrue(success)
        self.assertIn(f"Transfer of ${transfer_amount:.2f}", message)
        self.assertIn("My Savings (savings)", message)  # Display name
        self.assertIn("My Current (current)", message)  # Display name
        self.assertIn("completed successfully", message)
        self.assertIn(f"Transfer ID: {transfer_id}", message)


class TestTransferTracking(unittest.TestCase):
    """Test transfer tracking and history functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create accounts
        self.savings_account = Account("savings", 1000.0, 0, "Savings")
        self.current_account = Account("current", 500.0, 200.0, "Current")
        self.salary_account = Account("salary", 2000.0, 0, "Salary")
        
        self.user.accounts = [self.savings_account, self.current_account, self.salary_account]
        self.transfer_manager = TransferManager(self.user)
        
        # Execute some test transfers to create history
        self.transfer_manager.execute_transfer("savings", "current", 100.0, "Transfer 1")
        self.transfer_manager.execute_transfer("current", "salary", 50.0, "Transfer 2")
        self.transfer_manager.execute_transfer("salary", "savings", 200.0, "Transfer 3")
    
    def test_get_all_transfer_history(self):
        """Test getting complete transfer history"""
        transfers = self.transfer_manager.get_transfer_history()
        
        # Should have 6 transactions (2 per transfer: outgoing + incoming)
        self.assertEqual(len(transfers), 6)
        
        # Verify all are TransferTransaction instances
        for transfer in transfers:
            self.assertIsInstance(transfer, TransferTransaction)
    
    def test_get_transfer_history_by_account(self):
        """Test getting transfer history for specific account"""
        savings_transfers = self.transfer_manager.get_transfer_history("savings")
        
        # Savings account should have 2 transfers (1 outgoing, 1 incoming)
        self.assertEqual(len(savings_transfers), 2)
        
        # Verify all transfers involve savings account
        for transfer in savings_transfers:
            self.assertTrue(
                transfer.from_account == "savings" or transfer.to_account == "savings"
            )
    
    def test_get_transfer_history_by_nickname(self):
        """Test getting transfer history using account nickname"""
        current_transfers = self.transfer_manager.get_transfer_history("Current")
        
        # Current account should have 2 transfers (1 outgoing, 1 incoming)
        self.assertEqual(len(current_transfers), 2)
    
    def test_transfer_history_sorting(self):
        """Test that transfer history is sorted by date (most recent first)"""
        transfers = self.transfer_manager.get_transfer_history()
        
        # Verify sorting (most recent first)
        for i in range(len(transfers) - 1):
            self.assertGreaterEqual(transfers[i].date, transfers[i + 1].date)
    
    def test_get_transfer_by_id_success(self):
        """Test retrieving transfer by ID"""
        # Get a transfer ID from history
        transfers = self.transfer_manager.get_transfer_history()
        test_transfer_id = transfers[0].transfer_id
        
        found_transfer = self.transfer_manager.get_transfer_by_id(test_transfer_id)
        
        self.assertIsNotNone(found_transfer)
        self.assertEqual(found_transfer.transfer_id, test_transfer_id)
    
    def test_get_transfer_by_id_not_found(self):
        """Test retrieving non-existent transfer by ID"""
        found_transfer = self.transfer_manager.get_transfer_by_id("TXF-NOTFOUND")
        
        self.assertIsNone(found_transfer)
    
    def test_transfer_transaction_to_dict(self):
        """Test converting transfer transaction to dictionary for tracking"""
        transfers = self.transfer_manager.get_transfer_history()
        transfer = transfers[0]
        
        transfer_dict = transfer.to_dict()
        
        # Verify all required fields are present
        required_fields = [
            "amount", "transaction", "date", "from_account", 
            "to_account", "memo", "transfer_id", "is_outgoing"
        ]
        
        for field in required_fields:
            self.assertIn(field, transfer_dict)
        
        # Verify field values
        self.assertEqual(transfer_dict["transaction"], "transfer")
        self.assertEqual(transfer_dict["transfer_id"], transfer.transfer_id)
        self.assertIsInstance(transfer_dict["is_outgoing"], bool)
    
    def test_transfer_reference_consistency(self):
        """Test that transfer references are consistent between accounts"""
        # Execute a new transfer
        success, message, transfer_id = self.transfer_manager.execute_transfer(
            "savings", "current", 75.0, "Consistency test"
        )
        
        self.assertTrue(success)
        
        # Find the transfer transactions in both accounts
        savings_transfer = None
        current_transfer = None
        
        for transaction in self.savings_account.transactions:
            if isinstance(transaction, TransferTransaction) and transaction.transfer_id == transfer_id:
                savings_transfer = transaction
                break
        
        for transaction in self.current_account.transactions:
            if isinstance(transaction, TransferTransaction) and transaction.transfer_id == transfer_id:
                current_transfer = transaction
                break
        
        self.assertIsNotNone(savings_transfer)
        self.assertIsNotNone(current_transfer)
        
        # Verify consistency
        self.assertEqual(savings_transfer.transfer_id, current_transfer.transfer_id)
        self.assertEqual(savings_transfer.amount, current_transfer.amount)
        self.assertEqual(savings_transfer.memo, current_transfer.memo)
        self.assertEqual(savings_transfer.from_account, current_transfer.from_account)
        self.assertEqual(savings_transfer.to_account, current_transfer.to_account)
        
        # Verify direction flags
        self.assertTrue(savings_transfer.is_outgoing)
        self.assertFalse(current_transfer.is_outgoing)


class TestTransferIntegration(unittest.TestCase):
    """Integration tests for complete transfer workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User("testuser", "TestPass123", "test@example.com")
        
        # Create accounts with different configurations
        self.savings_account = Account("savings", 1500.0, 0, "Emergency Fund")
        self.current_account = Account("current", 300.0, 500.0, "Daily Spending")
        
        self.user.accounts = [self.savings_account, self.current_account]
        self.transfer_manager = TransferManager(self.user)
    
    def test_complete_transfer_workflow(self):
        """Test complete transfer workflow from validation to tracking"""
        transfer_amount = 400.0
        memo = "Monthly budget allocation"
        
        # Step 1: Validate transfer
        is_valid, message, from_acc, to_acc = self.transfer_manager.validate_transfer(
            "Emergency Fund", "Daily Spending", transfer_amount
        )
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "Transfer validation successful")
        
        # Step 2: Execute transfer
        success, exec_message, transfer_id = self.transfer_manager.execute_transfer(
            "Emergency Fund", "Daily Spending", transfer_amount, memo
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(transfer_id)
        
        # Step 3: Verify balance changes
        self.assertEqual(self.savings_account.balance, 1100.0)  # 1500 - 400
        self.assertEqual(self.current_account.balance, 700.0)   # 300 + 400
        
        # Step 4: Verify transaction tracking
        transfer_history = self.transfer_manager.get_transfer_history()
        self.assertEqual(len(transfer_history), 2)  # One outgoing, one incoming
        
        # Step 5: Verify transfer can be retrieved by ID
        retrieved_transfer = self.transfer_manager.get_transfer_by_id(transfer_id)
        self.assertIsNotNone(retrieved_transfer)
        self.assertEqual(retrieved_transfer.memo, memo)
    
    def test_multiple_transfers_tracking(self):
        """Test tracking multiple transfers between accounts"""
        transfers_data = [
            ("savings", "current", 200.0, "Transfer 1"),
            ("current", "savings", 50.0, "Transfer 2"),
            ("savings", "current", 100.0, "Transfer 3")
        ]
        
        transfer_ids = []
        
        # Execute multiple transfers
        for from_acc, to_acc, amount, memo in transfers_data:
            success, message, transfer_id = self.transfer_manager.execute_transfer(
                from_acc, to_acc, amount, memo
            )
            self.assertTrue(success)
            transfer_ids.append(transfer_id)
        
        # Verify all transfers are tracked
        all_transfers = self.transfer_manager.get_transfer_history()
        self.assertEqual(len(all_transfers), 6)  # 3 transfers × 2 transactions each
        
        # Verify each transfer can be retrieved by ID
        for transfer_id in transfer_ids:
            retrieved = self.transfer_manager.get_transfer_by_id(transfer_id)
            self.assertIsNotNone(retrieved)
        
        # Verify final balances
        expected_savings_balance = 1500.0 - 200.0 + 50.0 - 100.0  # 1250.0
        expected_current_balance = 300.0 + 200.0 - 50.0 + 100.0   # 550.0
        
        self.assertEqual(self.savings_account.balance, expected_savings_balance)
        self.assertEqual(self.current_account.balance, expected_current_balance)


if __name__ == '__main__':
    unittest.main()