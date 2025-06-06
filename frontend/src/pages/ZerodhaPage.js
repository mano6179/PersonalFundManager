import React from 'react';
import ZerodhaConnect from '../components/ZerodhaConnect';

const ZerodhaPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Zerodha Integration</h1>
      <p className="mb-6">
        Connect your Zerodha account to fetch your trading data, analyze your trades, and get insights into your trading performance.
      </p>
      
      <div className="grid grid-cols-1 gap-6">
        <ZerodhaConnect />
        
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Trading Analysis</h2>
          <p className="text-gray-600 dark:text-gray-300">
            Once you connect your Zerodha account, we'll analyze your trades and provide insights into your trading performance.
            This includes:
          </p>
          <ul className="list-disc pl-5 mt-2 space-y-1 text-gray-600 dark:text-gray-300">
            <li>Win/loss ratio analysis</li>
            <li>Sector-wise performance</li>
            <li>Holding period analysis</li>
            <li>Risk-reward ratio calculation</li>
            <li>Correlation with market sentiment</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ZerodhaPage;
