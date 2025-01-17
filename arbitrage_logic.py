import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ArbitrageLogic:
    def __init__(self, solana_interaction, dex_wrapper, wallet):
        self.solana_interaction = solana_interaction
        self.dex_wrapper = dex_wrapper
        self.wallet = wallet
        self.min_trade_size = 0.1  # Default value, can be updated later
        self.max_trade_size = 10.0  # Default value, can be updated later
        self.profit_threshold = 0.005  # 0.5% profit threshold
        self.token_pairs = ["SOL/USDC", "SOL/USDT", "BTC/USDC"]  # Initial token pairs

    def update_settings(self, config):
        self.min_trade_size = config.get('min_trade_size', self.min_trade_size)
        self.max_trade_size = config.get('max_trade_size', self.max_trade_size)
        self.profit_threshold = config.get('profit_threshold', self.profit_threshold)
        logger.info(f"Settings updated: min_trade_size={self.min_trade_size}, max_trade_size={self.max_trade_size}, profit_threshold={self.profit_threshold}")

    def find_opportunities(self):
        opportunities = []
        for pair in self.token_pairs:
            prices = self.dex_wrapper.get_prices(pair)
            if len(prices) < 2:
                logger.warning(f"Not enough prices for {pair} to compare, skipping...")
                continue
            
            dex_list = list(prices.keys())
            for i in range(len(dex_list)):
                for j in range(i + 1, len(dex_list)):
                    dex1, dex2 = dex_list[i], dex_list[j]
                    price1, price2 = prices[dex1], prices[dex2]
                    
                    profit1to2 = (price2 - price1) / price1
                    profit2to1 = (price1 - price2) / price2
                    
                    if profit1to2 > self.profit_threshold:
                        opportunities.append(self._create_opportunity(pair, dex1, dex2, price1, price2, profit1to2))
                        logger.info(f"Arbitrage opportunity found for {pair}: {profit1to2:.4f}% profit from {dex1} to {dex2}")
                    
                    if profit2to1 > self.profit_threshold:
                        opportunities.append(self._create_opportunity(pair, dex2, dex1, price2, price1, profit2to1))
                        logger.info(f"Arbitrage opportunity found for {pair}: {profit2to1:.4f}% profit from {dex2} to {dex1}")
                    
                    logger.debug(f"Compared {dex1} and {dex2} for {pair}: profit1to2={profit1to2:.4f}, profit2to1={profit2to1:.4f}")
        
        logger.debug(f"Total opportunities found: {len(opportunities)}")
        return opportunities

    def _create_opportunity(self, pair, buy_dex, sell_dex, buy_price, sell_price, profit):
        return {
            "pair": pair,
            "buy_dex": buy_dex,
            "sell_dex": sell_dex,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "profit_percentage": profit * 100,
            "dollar_profit": (sell_price - buy_price) * self.min_trade_size
        }

    def execute_trade(self, opportunity):
        logger.info(f"Executing trade: {opportunity}")
        
        try:
            # Buy from the cheaper DEX
            buy_amount = min(self.max_trade_size, max(self.min_trade_size, opportunity['dollar_profit'] / opportunity['profit_percentage'] * 100))
            buy_order = self.dex_wrapper.place_order(opportunity['buy_dex'], opportunity['pair'], buy_amount, "buy")
            
            # Sell on the more expensive DEX
            sell_amount = buy_amount * (1 - 0.001)  # Accounting for potential slippage
            sell_order = self.dex_wrapper.place_order(opportunity['sell_dex'], opportunity['pair'], sell_amount, "sell")
            
            # Calculate actual profit
            actual_profit = (sell_order['executed_price'] * sell_amount) - (buy_order['executed_price'] * buy_amount)
            
            logger.info(f"Trade executed successfully. Actual profit: {actual_profit}")
            return {
                "status": "success",
                "buy_order": buy_order,
                "sell_order": sell_order,
                "actual_profit": actual_profit
            }
        except Exception as e:
            logger.error(f"Error executing trade: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to execute trade: {str(e)}"
            }

    def self_replicate(self):
        logger.info("Starting self-replication process")
        new_pairs = []
        base_tokens = ["SOL", "BTC", "ETH", "LUNA", "AVAX"]
        quote_tokens = ["USDC", "USDT", "UST"]

        for base in base_tokens:
            for quote in quote_tokens:
                new_pair = f"{base}/{quote}"
                if new_pair not in self.token_pairs:
                    self.add_trading_pair(new_pair)
                    new_pairs.append(new_pair)

        logger.info(f"Self-replication complete. Added {len(new_pairs)} new trading pairs.")
        return new_pairs

    def add_trading_pair(self, new_pair):
        if new_pair not in self.token_pairs:
            self.token_pairs.append(new_pair)
            logger.info(f"Added new trading pair: {new_pair}")
        else:
            logger.warning(f"Trading pair {new_pair} already exists")

    def remove_trading_pair(self, pair):
        if pair in self.token_pairs:
            self.token_pairs.remove(pair)
            logger.info(f"Removed trading pair: {pair}")
        else:
            logger.warning(f"Trading pair {pair} not found")

    def get_trading_pairs(self):
        return self.token_pairs
