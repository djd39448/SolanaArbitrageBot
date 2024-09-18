from flask import Flask, render_template, jsonify, request
from solana_interaction import SolanaInteraction
from dex_wrapper import DEXWrapper
from arbitrage_logic import ArbitrageLogic
from wallet_integration import WalletIntegration
import json
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SERVER_NAME'] = None

# Load configuration
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
except Exception as e:
    logger.error(f"Error loading config file: {str(e)}")
    raise

# Initialize components
try:
    solana_interaction = SolanaInteraction(config['solana_rpc_url'])
    dex_wrapper = DEXWrapper()
    
    # Check if the private key is set in the environment variable
    env_private_key = os.environ.get('SOLANA_PRIVATE_KEY')
    if env_private_key:
        wallet = WalletIntegration(env_private_key)
    else:
        wallet = None
        logger.warning("No valid private key found. Some features may be limited.")
    
    arbitrage_logic = ArbitrageLogic(solana_interaction, dex_wrapper, wallet)
    arbitrage_logic.update_settings(config)
except Exception as e:
    logger.error(f"Error initializing components: {str(e)}")
    raise

@app.route('/')
def index():
    try:
        opportunities = arbitrage_logic.find_opportunities()
        logger.debug(f"Opportunities found: {opportunities}")
        
        current_settings = {
            "min_trade_size": arbitrage_logic.min_trade_size,
            "max_trade_size": arbitrage_logic.max_trade_size,
            "profit_threshold": arbitrage_logic.profit_threshold
        }
        
        trading_pairs = arbitrage_logic.get_trading_pairs()
        
        return render_template('index.html', opportunities=opportunities, settings=current_settings, trading_pairs=trading_pairs)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('error.html', error="An error occurred while fetching arbitrage opportunities. Please try again later."), 500

@app.route('/api/opportunities')
def get_opportunities():
    opportunities = arbitrage_logic.find_opportunities()
    return jsonify(opportunities)

@app.route('/api/execute_trade', methods=['POST'])
def execute_trade():
    if request.json and 'opportunity' in request.json:
        opportunity = request.json['opportunity']
        result = arbitrage_logic.execute_trade(opportunity)
        return jsonify(result)
    return jsonify({"error": "Invalid opportunity data"}), 400

@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    try:
        if request.json:
            new_settings = request.json
            if 'minTradeSize' in new_settings:
                config['min_trade_size'] = float(new_settings['minTradeSize'])
            if 'maxTradeSize' in new_settings:
                config['max_trade_size'] = float(new_settings['maxTradeSize'])
            if 'profitThreshold' in new_settings:
                config['profit_threshold'] = float(new_settings['profitThreshold'])
            
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
            
            # Update arbitrage logic with new settings
            arbitrage_logic.update_settings(config)
            
            logger.info("Settings updated successfully")
            return jsonify({"message": "Settings updated successfully"})
        else:
            return jsonify({"error": "No JSON data provided"}), 400
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({"error": "An error occurred while updating settings"}), 500

@app.route('/api/trading_pairs', methods=['GET'])
def get_trading_pairs():
    trading_pairs = arbitrage_logic.get_trading_pairs()
    return jsonify(trading_pairs)

@app.route('/api/add_trading_pair', methods=['POST'])
def add_trading_pair():
    if request.json and 'pair' in request.json:
        new_pair = request.json['pair']
        arbitrage_logic.add_trading_pair(new_pair)
        return jsonify({"message": f"Trading pair {new_pair} added successfully"})
    return jsonify({"error": "Invalid trading pair data"}), 400

@app.route('/api/remove_trading_pair', methods=['POST'])
def remove_trading_pair():
    if request.json and 'pair' in request.json:
        pair = request.json['pair']
        arbitrage_logic.remove_trading_pair(pair)
        return jsonify({"message": f"Trading pair {pair} removed successfully"})
    return jsonify({"error": "Invalid trading pair data"}), 400

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
