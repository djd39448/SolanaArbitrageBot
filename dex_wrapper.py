import requests
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 2

class DEXWrapper:
    def __init__(self, api_urls):
        self.api_urls = api_urls if isinstance(api_urls, list) else [api_urls]
        self.jupiter_api_url = 'https://price.jup.ag/v4/price'

    def get_raydium_price(self, token_pair):
        for api_url in self.api_urls:
            try:
                logger.debug(f"Fetching Raydium price for {token_pair} from {api_url}")
                response = requests.get(f"{api_url}/v2/main/price?pair={token_pair}")
                response.raise_for_status()
                data = response.json()
                
                if 'data' in data and 'price' in data['data']:
                    price = float(data['data']['price'])
                    logger.debug(f"Received Raydium price for {token_pair}: {price}")
                    return price
                else:
                    logger.warning(f"No price data found for {token_pair} in Raydium API response")
            except Exception as e:
                logger.error(f"Error fetching Raydium price for {token_pair} from {api_url}: {str(e)}")
        return None

    def get_jupiter_price(self, token_pair):
        try:
            base, quote = token_pair.split('/')
            logger.debug(f"Fetching Jupiter price for {token_pair}")
            response = requests.get(f"{self.jupiter_api_url}?ids={base}&vsToken={quote}")
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and base in data['data']:
                price = float(data['data'][base]['price'])
                logger.debug(f"Received Jupiter price for {token_pair}: {price}")
                return price
            else:
                logger.warning(f"No price data found for {token_pair} in Jupiter API response")
        except Exception as e:
            logger.error(f"Error fetching Jupiter price for {token_pair}: {str(e)}")
        return None

    def get_price(self, token_pair):
        for _ in range(MAX_RETRIES):
            raydium_price = self.get_raydium_price(token_pair)
            if raydium_price is not None:
                return raydium_price
            
            jupiter_price = self.get_jupiter_price(token_pair)
            if jupiter_price is not None:
                return jupiter_price
            
            time.sleep(RETRY_DELAY)
        
        logger.warning(f"Failed to fetch price for {token_pair} after {MAX_RETRIES} retries")
        return None

    def place_order(self, token_pair, amount, side):
        # Implement order placement logic here
        pass
