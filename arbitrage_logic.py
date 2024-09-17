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
        self.profit_threshold = 0.01  # Default value, can be updated later

    def update_settings(self, new_settings):
        self.min_trade_size = new_settings.get('min_trade_size', self.min_trade_size)
        self.max_trade_size = new_settings.get('max_trade_size', self.max_trade_size)
        self.profit_threshold = new_settings.get('profit_threshold', self.profit_threshold)

    def find_opportunities(self):
        opportunities = []
        token_pairs = ["SOL/USDC", "SOL/USDT", "BTC/USDC"]
        
        logger.debug("Starting to find arbitrage opportunities")
        for pair in token_pairs:
            try:
                logger.debug(f"Processing pair: {pair}")
                price = self.dex_wrapper.get_price(pair)
                
                if price is None:
                    logger.warning(f"Unable to fetch price for {pair}, skipping...")
                    continue
                
                logger.debug(f"Price for {pair}: {price}")
                
                reverse_pair = f"{pair.split('/')[1]}/{pair.split('/')[0]}"
                logger.debug(f"Processing reverse pair: {reverse_pair}")
                reverse_price = self.dex_wrapper.get_price(reverse_pair)
                
                if reverse_price is None:
                    logger.warning(f"Unable to fetch price for {reverse_pair}, skipping...")
                    continue
                
                logger.debug(f"Price for {reverse_pair}: {reverse_price}")
                
                if reverse_price != 0:
                    inverse_price = 1 / reverse_price
                    logger.debug(f"Inverse price for {reverse_pair}: {inverse_price}")
                    
                    if price < inverse_price:
                        profit = (inverse_price - price) / price
                        if profit > self.profit_threshold:
                            opportunity = {
                                "pair": pair,
                                "buy_price": price,
                                "sell_price": inverse_price,
                                "profit_percentage": profit * 100
                            }
                            opportunities.append(opportunity)
                            logger.debug(f"Opportunity found for {pair}: {profit * 100}% profit")
                    else:
                        logger.debug(f"No profitable opportunity for {pair}")
                else:
                    logger.warning(f"Invalid reverse price (0) for {reverse_pair}. Skipping.")
            except Exception as e:
                logger.error(f"Error processing pair {pair}: {str(e)}")
        
        logger.debug(f"Total opportunities found: {len(opportunities)}")
        return opportunities

    def execute_trade(self, opportunity):
        # This method remains unchanged
        buy_amount = max(min(self.min_trade_size, opportunity['buy_price']), self.max_trade_size)
        sell_amount = buy_amount * opportunity['sell_price']
        
        buy_order = self.dex_wrapper.place_order(opportunity['pair'], buy_amount, "buy")
        sell_order = self.dex_wrapper.place_order(opportunity['pair'], sell_amount, "sell")
        
        return {
            "buy_order": buy_order,
            "sell_order": sell_order,
            "estimated_profit": sell_amount - buy_amount
        }
