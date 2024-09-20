from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

class SolanaInteraction:
    def __init__(self, rpc_url):
        self.client = AsyncClient(rpc_url, Confirmed)

    async def get_balance(self, public_key):
        balance = await self.client.get_balance(public_key)
        return balance['result']['value'] / 10**9  # Convert lamports to SOL

    async def send_transaction(self, transaction):
        result = await self.client.send_transaction(transaction)
        return result['result']

    async def close(self):
        await self.client.close()
