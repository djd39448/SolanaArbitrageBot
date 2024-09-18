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

    def update_settings(self, new_settings):
        self.min_trade_size = new_settings.get('min_trade_size', self.min_trade_size)
        self.max_trade_size = new_settings.get('max_trade_size', self.max_trade_size)
        self.profit_threshold = new_settings.get('profit_threshold', self.profit_threshold)

    def find_opportunities(self):
        opportunities = []
        
        logger.debug("Starting to find arbitrage opportunities")
        for pair in self.token_pairs:
            try:
                logger.debug(f"Processing pair: {pair}")
                prices = self.dex_wrapper.get_prices(pair)
                
                if len(prices) < 1:
                    logger.warning(f"No prices available for {pair}, skipping...")
                    continue
                
                logger.debug(f"Prices for {pair}: {prices}")
                
                dex_list = list(prices.keys())
                for i in range(len(dex_list)):
                    for j in range(i + 1, len(dex_list)):
                        dex1, dex2 = dex_list[i], dex_list[j]
                        price1, price2 = prices[dex1], prices[dex2]
                        
                        # Check arbitrage opportunity from dex1 to dex2
                        profit1to2 = (price2 - price1) / price1
                        if profit1to2 > self.profit_threshold:
                            opportunity = self._create_opportunity(pair, dex1, dex2, price1, price2, profit1to2)
                            opportunities.append(opportunity)
                            logger.info(f"Arbitrage opportunity found for {pair}: {profit1to2:.4f}% profit from {dex1} to {dex2}")
                        
                        # Check arbitrage opportunity from dex2 to dex1
                        profit2to1 = (price1 - price2) / price2
                        if profit2to1 > self.profit_threshold:
                            opportunity = self._create_opportunity(pair, dex2, dex1, price2, price1, profit2to1)
                            opportunities.append(opportunity)
                            logger.info(f"Arbitrage opportunity found for {pair}: {profit2to1:.4f}% profit from {dex2} to {dex1}")
                        
                        logger.debug(f"Compared {dex1} and {dex2} for {pair}: profit1to2={profit1to2:.4f}, profit2to1={profit2to1:.4f}")
            except Exception as e:
                logger.error(f"Error processing pair {pair}: {str(e)}")
        
        logger.debug(f"Total opportunities found: {len(opportunities)}")
        return opportunities

    def _create_opportunity(self, pair, buy_dex, sell_dex, buy_price, sell_price, profit):
        # Assume a fixed trade size of 1 unit for simplicity
        trade_size = 1
        dollar_profit = (sell_price - buy_price) * trade_size
        return {
            "pair": pair,
            "buy_dex": buy_dex,
            "sell_dex": sell_dex,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "profit_percentage": profit * 100,
            "dollar_profit": dollar_profit
        }

    def execute_trade(self, opportunity):
        buy_amount = max(min(self.max_trade_size, opportunity['buy_price']), self.min_trade_size)
        sell_amount = buy_amount * opportunity['sell_price'] / opportunity['buy_price']
        
        logger.info(f"Executing trade: Buy {buy_amount} {opportunity['pair']} on {opportunity['buy_dex']} at {opportunity['buy_price']}")
        buy_order = self.dex_wrapper.place_order(opportunity['buy_dex'], opportunity['pair'], buy_amount, "buy")
        
        logger.info(f"Executing trade: Sell {sell_amount} {opportunity['pair']} on {opportunity['sell_dex']} at {opportunity['sell_price']}")
        sell_order = self.dex_wrapper.place_order(opportunity['sell_dex'], opportunity['pair'], sell_amount, "sell")
        
        estimated_profit = (sell_amount * opportunity['sell_price']) - (buy_amount * opportunity['buy_price'])
        logger.info(f"Estimated profit: {estimated_profit}")
        
        return {
            "buy_order": buy_order,
            "sell_order": sell_order,
            "estimated_profit": estimated_profit
        }

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

    def self_replicate(self):
        logger.info("Starting self-replication process")
        new_pairs = []
        for base in ["SOL", "BTC", "ETH"]:  # Add more base tokens as needed
            for quote in ["USDC", "USDT"]:
                new_pair = f"{base}/{quote}"
                if new_pair not in self.token_pairs:
                    new_pairs.append(new_pair)
        
        for pair in new_pairs:
            self.add_trading_pair(pair)
        
        logger.info(f"Self-replication complete. Added {len(new_pairs)} new trading pairs.")
        return new_pairs
