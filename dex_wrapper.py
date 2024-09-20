import requests
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 2
TIMEOUT = 10

class DEXWrapper:
    def __init__(self):
        self.raydium_api_url = 'https://api.raydium.io/v2/main/pairs'
        self.jupiter_api_url = 'https://price.jup.ag/v4/price'
        self.session = self._create_retry_session()
        self.token_addresses = {
            "SOL": "So11111111111111111111111111111111111111112",
            "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
            "BTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
        }

    def _create_retry_session(self):
        session = requests.Session()
        retries = Retry(total=MAX_RETRIES,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def get_raydium_price(self, token_pair):
        try:
            logger.debug(f"Fetching Raydium price for {token_pair}")
            response = self.session.get(self.raydium_api_url, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            base, quote = token_pair.split('/')
            pair_data = next((pair for pair in data if pair['name'] == f"{base}-{quote}"), None)
            
            if pair_data and 'price' in pair_data:
                price = float(pair_data['price'])
                logger.debug(f"Received Raydium price for {token_pair}: {price}")
                return price
            else:
                logger.warning(f"No price data found for {token_pair} in Raydium API response")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Raydium price for {token_pair}: {str(e)}")
        return None

    def get_jupiter_price(self, token_pair):
        try:
            base, quote = token_pair.split('/')
            logger.debug(f"Fetching Jupiter price for {token_pair}")
            response = self.session.get(f"{self.jupiter_api_url}?ids={base}&vsToken={quote}", timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and base in data['data']:
                price = float(data['data'][base]['price'])
                logger.debug(f"Received Jupiter price for {token_pair}: {price}")
                return price
            else:
                logger.warning(f"No price data found for {token_pair} in Jupiter API response")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Jupiter price for {token_pair}: {str(e)}")
        return None

    def get_prices(self, token_pair):
        prices = {}
        for _ in range(MAX_RETRIES):
            jupiter_price = self.get_jupiter_price(token_pair)
            if jupiter_price is not None:
                prices['jupiter'] = jupiter_price
            
            raydium_price = self.get_raydium_price(token_pair)
            if raydium_price is not None:
                prices['raydium'] = raydium_price
            
            if len(prices) >= 2:  # Return prices if we have at least two
                return prices
            
            time.sleep(RETRY_DELAY)
        
        logger.warning(f"Failed to fetch prices from both DEXes for {token_pair} after {MAX_RETRIES} retries")
        return prices

    def place_order(self, dex, token_pair, amount, side):
        logger.info(f"Placing {side} order on {dex} for {amount} {token_pair}")
        # This is a mock implementation. In a real scenario, you would interact with the DEX's API.
        executed_price = self.get_prices(token_pair)[dex]
        return {
            "status": "success",
            "order_id": f"mock_order_{dex}_{token_pair}_{side}",
            "executed_amount": amount,
            "executed_price": executed_price
        }
