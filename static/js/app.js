const app = Vue.createApp({
    data() {
        return {
            opportunities: [],
            settings: {
                minTradeSize: 0.1,
                maxTradeSize: 10,
                profitThreshold: 0.5
            },
            darkMode: false,
            tradingPairs: [],
            newPair: ''
        }
    },
    methods: {
        async fetchOpportunities() {
            const response = await fetch('/api/opportunities');
            this.opportunities = await response.json();
        },
        async executeTrade(opportunity) {
            const response = await fetch('/api/execute_trade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ opportunity })
            });
            const result = await response.json();
            alert(`Trade executed! Estimated profit: ${result.estimated_profit}`);
        },
        async updateSettings() {
            await fetch('/api/update_settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.settings)
            });
            alert('Settings updated!');
        },
        toggleDarkMode() {
            this.darkMode = !this.darkMode;
            document.body.classList.toggle('dark', this.darkMode);
            localStorage.setItem('darkMode', this.darkMode);
        },
        async fetchTradingPairs() {
            const response = await fetch('/api/trading_pairs');
            this.tradingPairs = await response.json();
        },
        async addTradingPair() {
            if (this.newPair) {
                await fetch('/api/add_trading_pair', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ pair: this.newPair })
                });
                this.newPair = '';
                await this.fetchTradingPairs();
            }
        },
        async removeTradingPair(pair) {
            await fetch('/api/remove_trading_pair', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pair })
            });
            await this.fetchTradingPairs();
        },
        async selfReplicate() {
            const response = await fetch('/api/self_replicate', {
                method: 'POST'
            });
            const result = await response.json();
            alert(result.message);
            await this.fetchTradingPairs();
        }
    },
    mounted() {
        this.fetchOpportunities();
        this.fetchTradingPairs();
        setInterval(this.fetchOpportunities, 30000); // Fetch every 30 seconds
        
        // Load dark mode preference from localStorage
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode !== null) {
            this.darkMode = JSON.parse(savedDarkMode);
            document.body.classList.toggle('dark', this.darkMode);
        }
    }
});

app.mount('#app');
