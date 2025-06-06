import React, { useState, useEffect, useCallback } from 'react';
import { useTheme } from '../context/ThemeContext';
import useWebSocket from 'react-use-websocket';
import { Box, Card, CardContent, Typography, Chip, Alert } from '@mui/material';

const MarketDataStream = () => {
    const { isDarkMode } = useTheme();
    const [marketData, setMarketData] = useState({});
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);

    // WebSocket setup
    const WS_URL = 'ws://localhost:8000/api/market/ws/client1';
    const { sendMessage, lastMessage, readyState } = useWebSocket(WS_URL, {
        onOpen: () => {
            console.log('WebSocket connection established');
            setIsConnected(true);
            setError(null);
            // Subscribe to default instruments
            sendMessage(JSON.stringify({
                type: 'subscribe',
                tokens: [256265, 260105] // Example: NIFTY 50 and BANKNIFTY
            }));
        },
        onClose: () => {
            console.log('WebSocket connection closed');
            setIsConnected(false);
        },
        onError: (error) => {
            console.error('WebSocket error:', error);
            setIsConnected(false);
            setError('Failed to connect to market data stream');
        },
        shouldReconnect: (closeEvent) => true,
        reconnectInterval: 3000,
    });

    // Handle incoming market data
    useEffect(() => {
        if (lastMessage !== null) {
            try {
                const data = JSON.parse(lastMessage.data);
                if (data.type === 'ticks') {
                    // Update market data state
                    setMarketData(prevData => ({
                        ...prevData,
                        ...data.data.reduce((acc, tick) => ({
                            ...acc,
                            [tick.instrument_token]: tick
                        }), {})
                    }));
                }
            } catch (e) {
                console.error('Error processing market data:', e);
            }
        }
    }, [lastMessage]);

    return (
        <Box sx={{ width: '100%', mb: 2 }}>
            <Card sx={{ 
                bgcolor: isDarkMode ? 'grey.900' : 'background.paper',
                borderRadius: 2
            }}>
                <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6" component="div">
                            Market Data Stream
                        </Typography>
                        <Chip 
                            label={isConnected ? 'Connected' : 'Disconnected'} 
                            color={isConnected ? 'success' : 'error'} 
                            size="small" 
                        />
                    </Box>
                    
                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
                    )}

                    <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))' }}>
                        {Object.entries(marketData).map(([token, data]) => (
                            <Card key={token} sx={{ bgcolor: isDarkMode ? 'grey.800' : 'grey.100' }}>
                                <CardContent>
                                    <Typography variant="subtitle2" color="textSecondary">
                                        Token: {token}
                                    </Typography>
                                    <Typography variant="h6">
                                        ₹{data.last_price.toFixed(2)}
                                    </Typography>
                                    <Typography variant="caption" color="textSecondary">
                                        Last Update: {new Date(data.timestamp).toLocaleTimeString()}
                                    </Typography>
                                </CardContent>
                            </Card>
                        ))}
                    </Box>
                </CardContent>
            </Card>
        </Box>
    );
};

export default MarketDataStream;
