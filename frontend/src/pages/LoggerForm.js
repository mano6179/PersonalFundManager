import React, { useState, useEffect } from 'react';
import { Button, Input, Select, Card, Textarea } from '../components/FormElements';
// import axios from 'axios'; // Uncomment when API integration is needed
import { useTheme } from '../context/ThemeContext';

const LoggerForm = () => {
  const { isDarkMode } = useTheme();
  const [logType, setLogType] = useState('weekly_profit');
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [time, setTime] = useState(() => {
    const now = new Date();
    return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  });
  const [formData, setFormData] = useState({
    // Weekly Profit fields
    profit: '',
    charges: '',
    funds_in_out: '0',  // Add this
    previous_nav: '',   // Add this

    // IV Tracker fields
    symbol: '',
    strike: '',
    expiry: '',
    iv: '',

    // Trade fields
    tradeType: 'entry',
    instrument: '',
    quantity: '',
    price: '',

    // Market Update fields
    title: '',
    content: '',
  });

  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(true);

  // Fetch logs when component mounts
  useEffect(() => {
    fetchLogs();
  }, []);

  // Fetch logs from localStorage
  const fetchLogs = async () => {
    try {
      setLogsLoading(true);
      const response = await fetch('http://localhost:8000/api/logs');
      
      if (!response.ok) {
        throw new Error('Failed to fetch logs');
      }

      const data = await response.json();
      setLogs(data);
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Failed to fetch logs');
    } finally {
      setLogsLoading(false);
    }
  };

  // Reset form fields when log type changes
  useEffect(() => {
    setFormData({
      // Weekly Profit fields
      profit: '',
      charges: '',
      funds_in_out: '0',  // Add this
      previous_nav: '',   // Add this

      // IV Tracker fields
      symbol: '',
      strike: '',
      expiry: '',
      iv: '',

      // Trade fields
      strategy: '',
      entry_exit: 'entry',
      quantity: '',
      premium: '',
      trade_date: new Date().toISOString().split('T')[0],
      notes: '',

      // Market Update fields
      title: '',
      content: '',
    });
  }, [logType]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccess(null);
    setError(null);
    setLoading(true);

    try {
      const timestamp = `${date}T${time}:00`;
      let newLog = {
        type: logType,
        timestamp
      };

      switch(logType) {
        case 'weekly_profit':
          newLog = {
            ...newLog,
            profit: parseFloat(formData.profit),
            charges: parseFloat(formData.charges),
            funds_in_out: parseFloat(formData.funds_in_out || 0),
            previous_nav: parseFloat(formData.previous_nav)
          };
          break;

        case 'iv_tracker':
          newLog = {
            ...newLog,
            symbol: formData.symbol,
            strike: parseFloat(formData.strike),
            expiry: formData.expiry,
            iv: parseFloat(formData.iv)
          };
          break;

        case 'trade':
          newLog = {
            ...newLog,
            symbol: formData.symbol,
            strategy: formData.strategy,
            entry_exit: formData.entry_exit,
            quantity: parseInt(formData.quantity),
            premium: parseFloat(formData.premium),
            date: formData.trade_date,
            notes: formData.notes
          };
          break;

        case 'market_update':
          newLog = {
            ...newLog,
            title: formData.title,
            content: formData.content
          };
          break;

        default:
          throw new Error('Invalid log type');
      }

      // Send to backend API
      const response = await fetch('http://localhost:8000/api/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newLog)
      });

      if (!response.ok) {
        throw new Error('Failed to submit log');
      }

      // Update local state with new data
      const result = await response.json();
      setLogs(prevLogs => [result, ...prevLogs]);
      setSuccess(`${getLogTypeLabel(logType)} logged successfully!`);
      
      // Reset form
      setFormData({
        profit: '',
        charges: '',
        funds_in_out: '0',
        previous_nav: '',
        // ... other fields reset
      });

    } catch (err) {
      console.error('Error submitting log:', err);
      setError('Failed to submit log. ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const getLogTypeLabel = (type) => {
    switch(type) {
      case 'weekly_profit': return 'Weekly Profit';
      case 'iv_tracker': return 'IV Tracker';
      case 'trade': return 'Trade';
      case 'market_update': return 'Market Update';
      default: return 'Log';
    }
  };

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
  };

  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  // Render log details based on log type
  const renderLogDetails = (log) => {
    switch(log.type) {
      case 'weekly_profit':
        return (
          <>
            <span className="mr-2">{formatCurrency(log.profit)}</span>
            <span className="text-accent-red">{formatCurrency(-log.charges)}</span>
          </>
        );
      case 'iv_tracker':
        return (
          <>
            <span className="mr-2">{log.symbol}</span>
            <span className="mr-2">{log.strike}</span>
            <span className="mr-2">{new Date(log.expiry).toLocaleDateString()}</span>
            <span>{log.iv}%</span>
          </>
        );
      case 'trade':
        return (
          <>
            <span className="mr-2">{log.symbol}</span>
            <span className="mr-2">{log.strategy}</span>
            <span className="mr-2">{log.entry_exit === 'entry' ? 'Entry' : 'Exit'}</span>
            <span className="mr-2">{log.quantity}</span>
            <span>{formatCurrency(log.premium)}</span>
          </>
        );
      case 'market_update':
        return (
          <>
            <span className="font-medium">{log.title}</span>
          </>
        );
      default:
        return <span>Unknown log type</span>;
    }
  };

  const renderFormFields = () => {
    switch(logType) {
      case 'weekly_profit':
        return (
          <>
            <Input
              label="Realized P&L"
              type="number"
              step="0.01"
              name="profit"
              value={formData.profit}
              onChange={handleInputChange}
              placeholder="Enter profit/loss amount"
              required
            />

            <Input
              label="Charges"
              type="number"
              step="0.01"
              name="charges"
              value={formData.charges}
              onChange={handleInputChange}
              placeholder="Enter charges amount"
              required
            />

            <Input
              label="Funds In/Out"
              type="number"
              step="0.01"
              name="funds_in_out"
              value={formData.funds_in_out}
              onChange={handleInputChange}
              placeholder="Enter funds (positive for inflow, negative for outflow)"
            />

            <Input
              label="Previous NAV"
              type="number"
              step="0.01"
              name="previous_nav"
              value={formData.previous_nav}
              onChange={handleInputChange}
              placeholder="Enter previous NAV value"
              required
            />
          </>
        );

      case 'iv_tracker':
        return (
          <>
            <Input
              label="Symbol"
              type="text"
              name="symbol"
              value={formData.symbol}
              onChange={handleInputChange}
              placeholder="Enter stock symbol (e.g., NIFTY, BANKNIFTY)"
              required
            />

            <Input
              label="Strike Price"
              type="number"
              step="0.01"
              name="strike"
              value={formData.strike}
              onChange={handleInputChange}
              placeholder="Enter strike price"
              required
            />

            <Input
              label="Expiry Date"
              type="date"
              name="expiry"
              value={formData.expiry}
              onChange={handleInputChange}
              required
            />

            <Input
              label="Implied Volatility (%)"
              type="number"
              step="0.01"
              name="iv"
              value={formData.iv}
              onChange={handleInputChange}
              placeholder="Enter IV percentage"
              required
            />
          </>
        );

      case 'trade':
        return (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Symbol"
                type="text"
                name="symbol"
                value={formData.symbol}
                onChange={handleInputChange}
                placeholder="Enter symbol (e.g., NIFTY, BANKNIFTY)"
                required
              />

              <Input
                label="Strategy"
                type="text"
                name="strategy"
                value={formData.strategy}
                onChange={handleInputChange}
                placeholder="Enter strategy (e.g., Iron Condor)"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Select
                label="Entry/Exit"
                name="entry_exit"
                value={formData.entry_exit}
                onChange={handleInputChange}
                options={[
                  { value: 'entry', label: 'Entry' },
                  { value: 'exit', label: 'Exit' }
                ]}
                required
              />

              <Input
                label="Quantity"
                type="number"
                name="quantity"
                value={formData.quantity}
                onChange={handleInputChange}
                placeholder="Enter quantity"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Premium"
                type="number"
                step="0.01"
                name="premium"
                value={formData.premium}
                onChange={handleInputChange}
                placeholder="Enter premium amount"
                required
              />

              <Input
                label="Date"
                type="date"
                name="trade_date"
                value={formData.trade_date}
                onChange={handleInputChange}
                required
              />
            </div>

            <Textarea
              label="Notes"
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              placeholder="Enter trade notes"
              rows={3}
            />
          </>
        );

      case 'market_update':
        return (
          <>
            <Input
              label="Title"
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="Enter update title"
              required
            />

            <Textarea
              label="Content"
              name="content"
              value={formData.content}
              onChange={handleInputChange}
              placeholder="Enter market update content"
              rows={6}
              required
            />
          </>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card title="Logger">
        <form onSubmit={handleSubmit}>
          <Select
            label="Log Type"
            value={logType}
            onChange={(e) => setLogType(e.target.value)}
            options={[
              { value: 'weekly_profit', label: 'Weekly Profit' },
              { value: 'iv_tracker', label: 'IV Tracker' },
              { value: 'trade', label: 'Trade' },
              { value: 'market_update', label: 'Market Update' }
            ]}
            required
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />

            <Input
              label="Time"
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              required
            />
          </div>

          {renderFormFields()}

          <div className="mt-6">
            <Button primary type="submit" disabled={loading}>
              {loading ? 'Submitting...' : `Submit ${getLogTypeLabel(logType)}`}
            </Button>
          </div>

          {error && (
            <div className={`mt-4 p-3 ${isDarkMode
              ? 'bg-red-900 border-red-700 text-white'
              : 'bg-red-100 border-red-400 text-red-700'} rounded border`}>
              {error}
            </div>
          )}

          {success && (
            <div className={`mt-4 p-3 ${isDarkMode
              ? 'bg-green-900 border-green-700 text-white'
              : 'bg-green-100 border-green-400 text-green-700'} rounded border`}>
              {success}
            </div>
          )}
        </form>
      </Card>

      {/* Recent Logs Table */}
      <Card title="Recent Logs">
        {logsLoading ? (
          <div className={`text-center py-4 ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
            Loading logs...
          </div>
        ) : logs.length === 0 ? (
          <div className={`text-center py-4 ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
            No logs found. Add your first log entry!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className={isDarkMode ? 'bg-neutral-light' : 'bg-neutral-lightest'}>
                <tr>
                  <th className={`px-4 py-3 text-left text-xs font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} uppercase tracking-wider`}>
                    Timestamp
                  </th>
                  <th className={`px-4 py-3 text-left text-xs font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} uppercase tracking-wider`}>
                    Type
                  </th>
                  <th className={`px-4 py-3 text-left text-xs font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} uppercase tracking-wider`}>
                    Details
                  </th>
                </tr>
              </thead>
              <tbody className={`divide-y ${isDarkMode ? 'divide-neutral-light bg-neutral-DEFAULT' : 'divide-neutral-lightest bg-white'}`}>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td className={`px-4 py-3 whitespace-nowrap text-sm ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
                      {formatTimestamp(log.timestamp)}
                    </td>
                    <td className={`px-4 py-3 whitespace-nowrap text-sm ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
                      {getLogTypeLabel(log.type)}
                    </td>
                    <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
                      {renderLogDetails(log)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};

export default LoggerForm;
