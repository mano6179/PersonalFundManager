import React, { useState, useEffect } from 'react';
import { tradeLogsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';
import { useTheme } from '../context/ThemeContext';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import { Card } from '../components/FormElements';

const TradeLog = () => {
    const { isDarkMode } = useTheme();
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user } = useAuth();

    useEffect(() => {
        fetchLogs();
    }, []);

    const fetchLogs = async () => {
        try {
            setLoading(true);
            const response = await tradeLogsAPI.getLogs();
            setLogs(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch trade logs');
            toast.error('Failed to fetch trade logs');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateLog = async (logData) => {
        try {
            const response = await tradeLogsAPI.createLog({
                ...logData,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
            });
            setLogs(prev => [response.data, ...prev]);
            toast.success('Trade log created successfully');
        } catch (err) {
            toast.error('Failed to create trade log');
        }
    };

    const handleUpdateLog = async (id, logData) => {
        try {
            const response = await tradeLogsAPI.updateLog(id, {
                ...logData,
                updated_at: new Date().toISOString()
            });
            setLogs(prev => 
                prev.map(log => 
                    log.id === id ? response.data : log
                )
            );
            toast.success('Trade log updated successfully');
        } catch (err) {
            toast.error('Failed to update trade log');
        }
    };

    const handleDeleteLog = async (id) => {
        try {
            await tradeLogsAPI.deleteLog(id);
            setLogs(prev => prev.filter(log => log.id !== id));
            toast.success('Trade log deleted successfully');
        } catch (err) {
            toast.error('Failed to delete trade log');
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold mb-6">Trade Logs</h1>
            
            {/* Create Log Form */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Create New Trade Log</h2>
                <form onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    handleCreateLog({
                        trade_id: formData.get('trade_id'),
                        symbol: formData.get('symbol'),
                        entry_date: formData.get('entry_date'),
                        entry_price: parseFloat(formData.get('entry_price')),
                        quantity: parseInt(formData.get('quantity')),
                        strategy: formData.get('strategy'),
                        notes: formData.get('notes'),
                        status: 'OPEN'
                    });
                    e.target.reset();
                }}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input
                            type="text"
                            name="trade_id"
                            placeholder="Trade ID"
                            className="border p-2 rounded"
                            required
                        />
                        <input
                            type="text"
                            name="symbol"
                            placeholder="Symbol"
                            className="border p-2 rounded"
                            required
                        />
                        <input
                            type="datetime-local"
                            name="entry_date"
                            className="border p-2 rounded"
                            required
                        />
                        <input
                            type="number"
                            name="entry_price"
                            placeholder="Entry Price"
                            step="0.01"
                            className="border p-2 rounded"
                            required
                        />
                        <input
                            type="number"
                            name="quantity"
                            placeholder="Quantity"
                            className="border p-2 rounded"
                            required
                        />
                        <select
                            name="strategy"
                            className="border p-2 rounded"
                            required
                        >
                            <option value="">Select Strategy</option>
                            <option value="Swing Trade">Swing Trade</option>
                            <option value="Day Trade">Day Trade</option>
                            <option value="Position Trade">Position Trade</option>
                        </select>
                        <textarea
                            name="notes"
                            placeholder="Notes"
                            className="border p-2 rounded md:col-span-2"
                        />
                        <button
                            type="submit"
                            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 md:col-span-2"
                        >
                            Create Trade Log
                        </button>
                    </div>
                </form>
            </div>

            {/* Logs List */}
            <div className="space-y-4">
                {logs.map(log => (
                    <div key={log.id} className="border p-4 rounded">
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="text-lg font-semibold">
                                    {log.symbol} - {log.trade_id}
                                </h3>
                                <div className="mt-2 grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-sm text-gray-600">Entry Date</p>
                                        <p>{new Date(log.entry_date).toLocaleString()}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-600">Entry Price</p>
                                        <p>₹{log.entry_price.toFixed(2)}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-600">Quantity</p>
                                        <p>{log.quantity}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-600">Strategy</p>
                                        <p>{log.strategy}</p>
                                    </div>
                                </div>
                                {log.notes && (
                                    <div className="mt-2">
                                        <p className="text-sm text-gray-600">Notes</p>
                                        <p>{log.notes}</p>
                                    </div>
                                )}
                                <div className="mt-2">
                                    <span className={`px-2 py-1 rounded text-sm ${
                                        log.status === 'OPEN' ? 'bg-green-200' :
                                        log.status === 'CLOSED' ? 'bg-red-200' :
                                        'bg-yellow-200'
                                    }`}>
                                        {log.status}
                                    </span>
                                </div>
                            </div>
                            <div className="flex space-x-2">
                                {log.status === 'OPEN' && (
                                    <button
                                        onClick={() => handleUpdateLog(log.id, {
                                            ...log,
                                            status: 'CLOSED',
                                            exit_date: new Date().toISOString(),
                                            exit_price: log.entry_price // This should be updated with actual exit price
                                        })}
                                        className="text-green-500 hover:text-green-700"
                                    >
                                        Close Trade
                                    </button>
                                )}
                                <button
                                    onClick={() => handleDeleteLog(log.id)}
                                    className="text-red-500 hover:text-red-700"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                        <div className="mt-2 text-sm text-gray-500">
                            Created: {new Date(log.created_at).toLocaleString()}
                            {log.updated_at !== log.created_at && (
                                <> • Updated: {new Date(log.updated_at).toLocaleString()}</>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TradeLog;