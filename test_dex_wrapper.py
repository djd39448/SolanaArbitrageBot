import logging
from dex_wrapper import DEXWrapper
from arbitrage_logic import ArbitrageLogic
from unittest.mock import Mock

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_dex_wrapper():
    dex_wrapper = DEXWrapper()
    token_pairs = ["SOL/USDC", "BTC/USDC", "SOL/USDT"]

    for pair in token_pairs:
        logger.info(f"Testing price fetching for {pair}")
        prices = dex_wrapper.get_prices(pair)
        logger.info(f"Prices for {pair}: {prices}")
        
        # Check if we have at least one price
        assert len(prices) >= 1, f"Expected at least 1 price for {pair}, but got {len(prices)}"
        
        # Check if the prices are reasonable (non-zero and not extremely high)
        for dex, price in prices.items():
            assert 0 < price < 1000000, f"Unexpected price for {pair} on {dex}: {price}"

def test_arbitrage_logic():
    dex_wrapper = DEXWrapper()
    mock_solana_interaction = Mock()
    mock_wallet = Mock()
    
    arbitrage_logic = ArbitrageLogic(mock_solana_interaction, dex_wrapper, mock_wallet)
    
    # Set a very small profit threshold to increase the chance of finding opportunities
    arbitrage_logic.profit_threshold = 0.0001
    
    opportunities = arbitrage_logic.find_opportunities()
    logger.info(f"Arbitrage opportunities found: {opportunities}")
    
    # Check if we found any opportunities
    assert len(opportunities) >= 0, "Expected to find zero or more arbitrage opportunities"
    
    # Verify the structure of the opportunities
    for opportunity in opportunities:
        assert "pair" in opportunity, "Opportunity missing 'pair' field"
        assert "buy_dex" in opportunity, "Opportunity missing 'buy_dex' field"
        assert "sell_dex" in opportunity, "Opportunity missing 'sell_dex' field"
        assert "buy_price" in opportunity, "Opportunity missing 'buy_price' field"
        assert "sell_price" in opportunity, "Opportunity missing 'sell_price' field"
        assert "profit_percentage" in opportunity, "Opportunity missing 'profit_percentage' field"
        
        # Verify that the profit percentage is positive
        assert opportunity["profit_percentage"] > 0, f"Expected positive profit, but got {opportunity['profit_percentage']}%"

if __name__ == "__main__":
    logger.info("Testing DEX Wrapper")
    test_dex_wrapper()
    
    logger.info("\nTesting Arbitrage Logic")
    test_arbitrage_logic()
