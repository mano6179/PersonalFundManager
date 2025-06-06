import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from '../config';

const ZerodhaConnect = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [accessToken, setAccessToken] = useState('');
  const [profile, setProfile] = useState(null);
  const [holdings, setHoldings] = useState([]);
  const [positions, setPositions] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Check if we have a token in localStorage
  useEffect(() => {
    const token = localStorage.getItem('zerodhaAccessToken');
    if (token) {
      setAccessToken(token);
      setIsConnected(true);
      fetchZerodhaData(token);
    }
  }, []);

  // Handle the redirect from Zerodha with request_token
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const requestToken = urlParams.get('request_token');
    
    if (requestToken) {
      handleRequestToken(requestToken);
    }
  }, [handleRequestToken]);

  const handleRequestToken = async (requestToken) => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.get(`${API_URL}/api/zerodha/callback?request_token=${requestToken}`);
      
      if (response.data && response.data.access_token) {
        const token = response.data.access_token;
        setAccessToken(token);
        localStorage.setItem('zerodhaAccessToken', token);
        setIsConnected(true);
        
        // Fetch data with the new token
        fetchZerodhaData(token);
      }
    } catch (err) {
      console.error('Error handling request token:', err);
      setError('Failed to authenticate with Zerodha. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchZerodhaData = async (token) => {
    try {
      setLoading(true);
      
      // Set the token first
      await axios.post(`${API_URL}/api/zerodha/set-token`, {
        api_key: '2o2hlqr9zojrs4uo',
        api_secret: '',
        access_token: token
      });
      
      // Fetch profile
      const profileResponse = await axios.get(`${API_URL}/api/zerodha/profile`);
      setProfile(profileResponse.data);
      
      // Fetch holdings
      const holdingsResponse = await axios.get(`${API_URL}/api/zerodha/holdings`);
      setHoldings(holdingsResponse.data);
      
      // Fetch positions
      const positionsResponse = await axios.get(`${API_URL}/api/zerodha/positions`);
      setPositions(positionsResponse.data);
      
    } catch (err) {
      console.error('Error fetching Zerodha data:', err);
      setError('Failed to fetch data from Zerodha. Your session might have expired.');
      
      // If unauthorized, clear the token
      if (err.response && err.response.status === 401) {
        localStorage.removeItem('zerodhaAccessToken');
        setIsConnected(false);
        setAccessToken('');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = () => {
    window.location.href = `${API_URL}/api/zerodha/login`;
  };

  const handleDisconnect = async () => {
    try {
      setLoading(true);
      
      // Logout from Zerodha
      await axios.post(`${API_URL}/api/zerodha/logout`);
      
      // Clear local storage and state
      localStorage.removeItem('zerodhaAccessToken');
      setIsConnected(false);
      setAccessToken('');
      setProfile(null);
      setHoldings([]);
      setPositions({});
      
    } catch (err) {
      console.error('Error disconnecting from Zerodha:', err);
      setError('Failed to disconnect from Zerodha.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Zerodha Integration</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center items-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <>
          {!isConnected ? (
            <div className="text-center">
              <p className="mb-4">Connect your Zerodha account to fetch your trading data</p>
              <button
                onClick={handleConnect}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                Connect to Zerodha
              </button>
            </div>
          ) : (
            <div>
              {profile && (
                <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded">
                  <h3 className="font-semibold mb-2">Connected Account</h3>
                  <p>User: {profile.user_name || profile.user_id}</p>
                  <p>Email: {profile.email}</p>
                </div>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <h3 className="font-semibold mb-2">Holdings ({holdings.length})</h3>
                  {holdings.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead>
                          <tr>
                            <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                            <th className="px-2 py-1 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                            <th className="px-2 py-1 text-right text-xs font-medium text-gray-500 uppercase">P&L</th>
                          </tr>
                        </thead>
                        <tbody>
                          {holdings.map((holding, index) => (
                            <tr key={index} className={index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-700' : ''}>
                              <td className="px-2 py-1 text-sm">{holding.tradingsymbol}</td>
                              <td className="px-2 py-1 text-sm text-right">{holding.quantity}</td>
                              <td className={`px-2 py-1 text-sm text-right ${holding.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {holding.pnl.toFixed(2)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No holdings found</p>
                  )}
                </div>
                
                <div>
                  <h3 className="font-semibold mb-2">Positions</h3>
                  {positions.net && positions.net.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead>
                          <tr>
                            <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                            <th className="px-2 py-1 text-right text-xs font-medium text-gray-500 uppercase">Qty</th>
                            <th className="px-2 py-1 text-right text-xs font-medium text-gray-500 uppercase">P&L</th>
                          </tr>
                        </thead>
                        <tbody>
                          {positions.net.map((position, index) => (
                            <tr key={index} className={index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-700' : ''}>
                              <td className="px-2 py-1 text-sm">{position.tradingsymbol}</td>
                              <td className="px-2 py-1 text-sm text-right">{position.quantity}</td>
                              <td className={`px-2 py-1 text-sm text-right ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {position.pnl.toFixed(2)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No positions found</p>
                  )}
                </div>
              </div>
              
              <div className="text-center mt-4">
                <button
                  onClick={() => fetchZerodhaData(accessToken)}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2"
                >
                  Refresh Data
                </button>
                <button
                  onClick={handleDisconnect}
                  className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                >
                  Disconnect
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ZerodhaConnect;
