import asyncio
import sys
import os
import logging
from datetime import datetime, date
from decimal import Decimal

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.repositories.database import DatabaseRepository
from app.models.nav import NAVRecord
from app.models.zerodha import ZerodhaHolding, ZerodhaPosition, ZerodhaTrade
from app.exceptions.database_exceptions import DatabaseException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_operations():
    try:
        # Test investor creation
        investor_data = {
            "id": 1,
            "name": "Test Investor",
            "email": "test@example.com"
        }
        logger.info("Testing investor creation...")
        created_investor = await DatabaseRepository.create_investor(investor_data)
        logger.info(f"Created investor: {created_investor}")

        # Test NAV record creation
        nav_record = NAVRecord(
            id=1,
            investor_id=1,
            date=date.today(),
            total_value=Decimal("100000.00"),
            cash_balance=Decimal("20000.00"),
            equity_value=Decimal("70000.00"),
            other_assets=Decimal("10000.00")
        )
        logger.info("Testing NAV record creation...")
        saved_nav = await DatabaseRepository.save_nav_record(nav_record)
        logger.info(f"Saved NAV record: {saved_nav}")

        # Test trade creation
        trade = ZerodhaTrade(
            trade_id="TEST123",
            order_id="ORDER123",
            exchange="NSE",
            tradingsymbol="RELIANCE",
            trade_type="BUY",
            quantity=10,
            price=Decimal("2500.00"),
            trade_date=datetime.now()
        )
        logger.info("Testing trade creation...")
        await DatabaseRepository.save_trades([trade], "TEST_USER")
        
        # Test trade retrieval
        trades = await DatabaseRepository.get_trades("TEST_USER")
        logger.info(f"Retrieved trades: {trades}")

        # Test holdings
        holding = ZerodhaHolding(
            tradingsymbol="RELIANCE",
            exchange="NSE",
            isin="INE002A01018",
            quantity=10,
            average_price=Decimal("2500.00"),
            last_price=Decimal("2600.00"),
            pnl=Decimal("1000.00")
        )
        logger.info("Testing holdings update...")
        await DatabaseRepository.update_holdings([holding], "TEST_USER")
        
        holdings = await DatabaseRepository.get_holdings("TEST_USER")
        logger.info(f"Retrieved holdings: {holdings}")

        logger.info("All database operations completed successfully!")
        
    except DatabaseException as e:
        logger.error(f"Database operation failed: {e.message}")
        logger.error(f"Operation: {e.operation}")
        if e.original_error:
            logger.error(f"Original error: {str(e.original_error)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_database_operations())
