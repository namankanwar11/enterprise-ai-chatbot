# external_api_mock.py
from typing import Dict, Optional

class CustomerServiceAPI:
    """
    Mocks an external API for fetching customer data.
    This simulates a backend server connection.
    """
    
    # Mock database of user accounts
    _mock_accounts: Dict[str, Dict[str, str]] = {
        "user123": {
            "status": "Active",
            "last_payment": "2024-12-01",
            "balance": "$0.00",
            "name": "Naman"
        },
        "user999": {
            "status": "Suspended",
            "last_payment": "2024-06-15",
            "balance": "$120.50 (Overdue)",
            "name": "Alex"
        },
        "test": {
            "status": "Active",
            "last_payment": "2024-12-05",
            "balance": "$0.00",
            "name": "Tester"
        }
    }

    def fetch_user_data(self, user_id: str) -> Optional[Dict[str, str]]:
        """Fetches account details if the ID exists."""
        user_id = user_id.lower().strip()
        return self._mock_accounts.get(user_id)

    def get_account_status(self, user_id: str) -> str:
        """Returns a formatted status message."""
        data = self.fetch_user_data(user_id)
        
        if not data:
            return "❌ User ID not found."
        
        if data["status"] == "Active":
            return f"✅ Account Active. (Balance: {data['balance']})"
        else:
            return f"⚠️ Account {data['status']}. (Balance: {data['balance']})"