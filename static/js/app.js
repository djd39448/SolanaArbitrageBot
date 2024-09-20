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
            newPair: '',
            opportunitiesInterval: null
        }
    },
    methods: {
        async fetchOpportunities() {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
                const response = await fetch('/api/opportunities', { signal: controller.signal });
                clearTimeout(timeoutId);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const opportunities = await response.json();
                this.opportunities = opportunities;
                console.log('Opportunities updated:', opportunities);
            } catch (error) {
                console.error('Error fetching opportunities:', error);
            }
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
        this.fetchOpportunities(); // Fetch immediately on mount
        this.opportunitiesInterval = setInterval(this.fetchOpportunities, 5000); // Then every 5 seconds
        this.fetchTradingPairs();
        
        // Load dark mode preference from localStorage
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode !== null) {
            this.darkMode = JSON.parse(savedDarkMode);
            document.body.classList.toggle('dark', this.darkMode);
        }
    },
    beforeUnmount() {
        clearInterval(this.opportunitiesInterval);
    }
});

app.mount('#app');
