const express = require('express');
const { PublicKey, Connection } = require("@solana/web3.js");
const { WhirlpoolContext, ORCA_WHIRLPOOL_PROGRAM_ID, Percentage } = require("@orca-so/whirlpools-sdk");
const Decimal = require('decimal.js');

const app = express();
const port = 3000;

// Initialize Solana connection
const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");

// Initialize WhirlpoolContext
const ctx = WhirlpoolContext.withConnection(connection, new PublicKey(ORCA_WHIRLPOOL_PROGRAM_ID));

app.use(express.json());

app.get('/price', async (req, res) => {
    try {
        const { inputToken, outputToken, amount } = req.query;
        
        // Convert amount to Decimal
        const inputAmount = new Decimal(amount);
        
        // Fetch the whirlpool for the token pair
        const whirlpools = await ctx.fetcher.listWhirlpools();
        const whirlpool = whirlpools.find(pool => 
            pool.tokenMintA.equals(new PublicKey(inputToken)) && 
            pool.tokenMintB.equals(new PublicKey(outputToken))
        );
        
        if (!whirlpool) {
            throw new Error('Whirlpool not found for the given token pair');
        }
        
        // Get the quote
        const quote = await whirlpool.getQuote(inputAmount, Percentage.fromFraction(1, 100), true);
        
        // Calculate the price
        const price = quote.estimatedAmountOut.toNumber() / inputAmount.toNumber();
        
        res.json({ price });
    } catch (error) {
        console.error('Error fetching price:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.listen(port, () => {
    console.log(`Orca service listening at http://localhost:${port}`);
});
