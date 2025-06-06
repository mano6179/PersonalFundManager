import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Card } from '../components/FormElements';
import MarketDataStream from '../components/MarketDataStream';

const MarketUpdates = () => {
  const { isDarkMode } = useTheme();
  const [marketUpdates, setMarketUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initialize localStorage with mock data if it doesn't exist
    initializeMarketUpdates();
    fetchMarketUpdates();
  }, []);

  const initializeMarketUpdates = () => {
    // Check if data already exists in localStorage
    const storedLogsJSON = localStorage.getItem('steadyGainsLogs');

    if (!storedLogsJSON) {
      // If no data exists, initialize with mock data
      const mockUpdates = [
        {
          id: 1,
          type: 'market_update',
          timestamp: '2025-05-05T22:42:00',
          title: 'Caution creeping in?',
          content: 'Markets saw muted movement today with NIFTY forming a small-bodied candle, signaling indecision. BANKNIFTY faced selling pressure intraday but managed to recover part of its losses by close.\n\nOption chain suggests resistance building near 24,500 and support getting weaker below 24,200. The Put-Call Ratio remained steady at 0.9, showing no strong directional bias.\n\nFIIs stayed mostly inactive on the options front, while Proprietary traders added long calls. Clients were seen shorting puts, indicating retail is still holding bullish expectations.\n\nIn the futures market, FIIs were marginal net buyers, while clients added to short positions. DII participation was flat. FIIs also logged ₹2,600 Cr of inflows in the cash segment, showing underlying buying strength.\n\nDespite the lack of a clear trend today, cautious positioning and resistance near current levels suggest staying light. No strong trade setups unless there\'s a clean break either way.'
        },
        {
          id: 2,
          type: 'market_update',
          timestamp: '2025-05-02T23:07:00',
          title: 'Volatility brewing?',
          content: 'NIFTY ended flat after swinging both sides, forming a Doji on the daily chart—a classic sign of uncertainty. BANKNIFTY underperformed slightly, unable to reclaim the 52,000 level.\n\nOpen Interest built up on both calls and puts across key strikes, indicating an upcoming move. Resistance still looms around 24,500. PCR cooled off to 0.75, implying growing nervousness.\n\nFIIs remained net buyers of puts, possibly as insurance. Proprietary traders built long straddles. Retail clients increased short calls, reflecting expectations of a ceiling in place.\n\nOn the futures side, positions were largely unchanged. FIIs added ₹1,800 Cr in the cash market, maintaining a steady inflow trend.\n\nThe setup suggests markets are coiling for a move. Direction is unclear, but volatility strategies like long straddles or strangles could be worth exploring with tight risk controls.'
        },
        {
          id: 3,
          type: 'market_update',
          timestamp: '2025-05-01T22:23:00',
          title: 'Profit booking or pause?',
          content: 'After a sharp rally, NIFTY paused with a small red candle, showing signs of fatigue. BANKNIFTY followed suit, failing to hold higher levels by the close.\n\nOptions data indicates resistance stacking up at 24,400 and 24,500, while support near 24,100 is seeing unwinding. PCR dropped from 1.1 to 0.85, signaling increased caution.\n\nFIIs stayed light in the options space today, while Proprietary traders hedged via put buying. Clients took the contrarian view, selling both puts and calls aggressively.\n\nFutures activity was neutral. Cash market action saw mild FII selling to the tune of ₹700 Cr—nothing alarming but a change in tone.\n\nGiven the signals, short-term consolidation or dip cannot be ruled out. Better to wait for confirmation before jumping into fresh trades.'
        },
        {
          id: 4,
          type: 'market_update',
          timestamp: '2025-04-30T22:38:00',
          title: 'Strong open, weak close',
          content: 'Markets opened strong on global cues but couldn\'t sustain gains. NIFTY closed with an upper wick, forming a potential reversal signal. BANKNIFTY showed more weakness and lost key support.\n\nOpen Interest built up rapidly on the call side, especially at 24,400 and 24,500. PCR dipped sharply to 0.7, hinting at sentiment turning cautious.\n\nFIIs added both calls and puts, with a slight tilt toward puts. Proprietary desks were net neutral, while clients leaned heavily on selling puts, reflecting misplaced optimism.\n\nIn futures, FIIs trimmed some longs and DIIs stepped in with buying. The cash segment saw ₹1,200 Cr of FII inflows, but that failed to lift sentiment.\n\nThe intraday reversal suggests that markets may be preparing for a short-term pullback. It\'s a good zone to protect gains and possibly consider hedged bearish setups.'
        }
      ];

      // Save to localStorage
      localStorage.setItem('steadyGainsLogs', JSON.stringify(mockUpdates));
    }
  };

  const fetchMarketUpdates = async () => {
    try {
      setLoading(true);

      // Get logs from localStorage
      const storedLogsJSON = localStorage.getItem('steadyGainsLogs');

      if (storedLogsJSON) {
        const allLogs = JSON.parse(storedLogsJSON);

        // Filter to get only market_update logs and sort by timestamp (newest first)
        const updates = allLogs
          .filter(log => log.type === 'market_update')
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        setMarketUpdates(updates);
        setError(null);
      } else {
        // If no logs in localStorage, use mock data
        const mockUpdates = [
          {
            id: 1,
            type: 'market_update',
            timestamp: '2025-05-05T22:42:00',
            title: 'Caution creeping in?',
            content: 'Markets saw muted movement today with NIFTY forming a small-bodied candle, signaling indecision. BANKNIFTY faced selling pressure intraday but managed to recover part of its losses by close.\n\nOption chain suggests resistance building near 24,500 and support getting weaker below 24,200. The Put-Call Ratio remained steady at 0.9, showing no strong directional bias.\n\nFIIs stayed mostly inactive on the options front, while Proprietary traders added long calls. Clients were seen shorting puts, indicating retail is still holding bullish expectations.\n\nIn the futures market, FIIs were marginal net buyers, while clients added to short positions. DII participation was flat. FIIs also logged ₹2,600 Cr of inflows in the cash segment, showing underlying buying strength.\n\nDespite the lack of a clear trend today, cautious positioning and resistance near current levels suggest staying light. No strong trade setups unless there\'s a clean break either way.'
          },
          {
            id: 2,
            type: 'market_update',
            timestamp: '2025-05-02T23:07:00',
            title: 'Volatility brewing?',
            content: 'NIFTY ended flat after swinging both sides, forming a Doji on the daily chart—a classic sign of uncertainty. BANKNIFTY underperformed slightly, unable to reclaim the 52,000 level.\n\nOpen Interest built up on both calls and puts across key strikes, indicating an upcoming move. Resistance still looms around 24,500. PCR cooled off to 0.75, implying growing nervousness.\n\nFIIs remained net buyers of puts, possibly as insurance. Proprietary traders built long straddles. Retail clients increased short calls, reflecting expectations of a ceiling in place.\n\nOn the futures side, positions were largely unchanged. FIIs added ₹1,800 Cr in the cash market, maintaining a steady inflow trend.\n\nThe setup suggests markets are coiling for a move. Direction is unclear, but volatility strategies like long straddles or strangles could be worth exploring with tight risk controls.'
          },
          {
            id: 3,
            type: 'market_update',
            timestamp: '2025-05-01T22:23:00',
            title: 'Profit booking or pause?',
            content: 'After a sharp rally, NIFTY paused with a small red candle, showing signs of fatigue. BANKNIFTY followed suit, failing to hold higher levels by the close.\n\nOptions data indicates resistance stacking up at 24,400 and 24,500, while support near 24,100 is seeing unwinding. PCR dropped from 1.1 to 0.85, signaling increased caution.\n\nFIIs stayed light in the options space today, while Proprietary traders hedged via put buying. Clients took the contrarian view, selling both puts and calls aggressively.\n\nFutures activity was neutral. Cash market action saw mild FII selling to the tune of ₹700 Cr—nothing alarming but a change in tone.\n\nGiven the signals, short-term consolidation or dip cannot be ruled out. Better to wait for confirmation before jumping into fresh trades.'
          },
          {
            id: 4,
            type: 'market_update',
            timestamp: '2025-04-30T22:38:00',
            title: 'Strong open, weak close',
            content: 'Markets opened strong on global cues but couldn\'t sustain gains. NIFTY closed with an upper wick, forming a potential reversal signal. BANKNIFTY showed more weakness and lost key support.\n\nOpen Interest built up rapidly on the call side, especially at 24,400 and 24,500. PCR dipped sharply to 0.7, hinting at sentiment turning cautious.\n\nFIIs added both calls and puts, with a slight tilt toward puts. Proprietary desks were net neutral, while clients leaned heavily on selling puts, reflecting misplaced optimism.\n\nIn futures, FIIs trimmed some longs and DIIs stepped in with buying. The cash segment saw ₹1,200 Cr of FII inflows, but that failed to lift sentiment.\n\nThe intraday reversal suggests that markets may be preparing for a short-term pullback. It\'s a good zone to protect gains and possibly consider hedged bearish setups.'
          }
        ];

        setMarketUpdates(mockUpdates);
      }
    } catch (err) {
      console.error('Error fetching market updates:', err);
      setError('Failed to load market updates. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-IN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`p-4 ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'}`}>
      <h1 className="text-2xl font-bold mb-4">Market Updates</h1>
      
      {/* Real-time Market Data */}
      <div className="mb-6">
        <MarketDataStream />
      </div>

      {/* Market Updates List */}
      <Card title="Market Updates">
        {loading ? (
          <div className={`text-center py-4 ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
            Loading market updates...
          </div>
        ) : error ? (
          <div className={`text-center py-4 ${isDarkMode ? 'text-accent-red' : 'text-accent-red'}`}>
            {error}
          </div>
        ) : marketUpdates.length === 0 ? (
          <div className={`text-center py-4 ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
            No market updates available.
          </div>
        ) : (
          <div className="space-y-6">
            {marketUpdates.map((update) => (
              <div
                key={update.id}
                className={`p-4 rounded-sm border ${
                  isDarkMode
                    ? 'border-neutral-light bg-neutral-DEFAULT'
                    : 'border-neutral-lightest bg-white'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-3">
                  <h3 className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                    {update.title}
                  </h3>
                  <span className={`text-sm mt-1 sm:mt-0 ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-light'}`}>
                    {formatTimestamp(update.timestamp)}
                  </span>
                </div>
                <p className={`${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} whitespace-pre-line`}>
                  {update.content}
                </p>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default MarketUpdates;
