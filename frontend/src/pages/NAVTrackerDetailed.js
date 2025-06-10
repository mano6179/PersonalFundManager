import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import NAVGraph from '../components/NAVGraph';
import NAVDataTable from '../components/NAVDataTable';

const NAVTrackerDetailed = () => {
  const { isDarkMode } = useTheme();
  const [summaryData, setSummaryData] = useState({
    fundValue: 0,
    currentNAV: 0,
    outstandingUnits: 0,
    totalInvestment: 0,
    totalProfit: 0,
    growthPercentage: 0
  });

  useEffect(() => {
    const fetchSummaryData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/nav/history');
        if (!response.ok) {
          throw new Error('Failed to fetch NAV data');
        }
        const data = await response.json();
        
        if (data && data.length > 0) {
          const latestRecord = data[data.length - 1];
          const initialRecord = data[0];
          
          // Calculate total funds in/out (total investment)
          const totalInvestment = data.reduce((sum, record) => sum + (record.funds_in_out || 0), 0);
          
          // Get the latest funds in/out and units change
          const latestFundsInOut = latestRecord.funds_in_out || 0;
          const latestUnitsChange = latestRecord.units_change || 0;
          
          // Calculate current fund value including latest funds in/out
          const currentFundValue = (latestRecord.fund_value || 0) + latestFundsInOut;
          
          // Calculate current outstanding units including latest units change
          const currentOutstandingUnits = (latestRecord.outstanding_units || 0) + latestUnitsChange;
          
          // Calculate total profit based on current fund value
          const totalProfit = currentFundValue - totalInvestment;
          
          // Calculate growth percentage based on current fund value
          const growthPercentage = totalInvestment !== 0 ? ((currentFundValue / totalInvestment) - 1) * 100 : 0;
          
          setSummaryData({
            fundValue: currentFundValue,
            currentNAV: latestRecord.nav_value || 0,
            outstandingUnits: currentOutstandingUnits,
            totalInvestment,
            totalProfit,
            growthPercentage
          });
        }
      } catch (error) {
        console.error('Error fetching summary data:', error);
      }
    };

    fetchSummaryData();
  }, []);

  // Format currency with null check
  const formatCurrency = (value) => {
    if (value === undefined || value === null) {
      return '₹ 0.00';
    }
    return `₹ ${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <div className="space-y-6">
      <div className={`p-6 rounded-sm shadow-card ${isDarkMode ? 'bg-primary-DEFAULT border border-primary-light' : 'bg-white border border-neutral-lightest'}`}>
        <h2 className={`text-2xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>NAV</h2>
        <p className={`${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
          Track the Net Asset Value of your investments over time. The graph will automatically scale as new data points are added weekly.
        </p>
      </div>

      {/* NAV Graph */}
      <NAVGraph />

      {/* Summary Section */}
      <div className={`p-6 rounded-sm shadow-card ${isDarkMode ? 'bg-neutral-DEFAULT border border-neutral-light' : 'bg-white border border-neutral-lightest'}`}>
        <h3 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className={`p-4 rounded-sm ${isDarkMode ? 'bg-neutral-light' : 'bg-neutral-lightest'}`}>
            <p className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>Fund Value</p>
            <p className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
              {formatCurrency(summaryData.fundValue)}
            </p>
          </div>
          <div className={`p-4 rounded-sm ${isDarkMode ? 'bg-neutral-light' : 'bg-neutral-lightest'}`}>
            <p className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>Current NAV</p>
            <p className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
              {formatCurrency(summaryData.currentNAV)}
            </p>
          </div>
          <div className={`p-4 rounded-sm ${isDarkMode ? 'bg-neutral-light' : 'bg-neutral-lightest'}`}>
            <p className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>Outstanding Units</p>
            <p className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
              {(summaryData.outstandingUnits || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </p>
          </div>
          <div className={`p-4 rounded-sm ${isDarkMode ? 'bg-neutral-light' : 'bg-neutral-lightest'}`}>
            <p className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>Total Investment</p>
            <p className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
              {formatCurrency(summaryData.totalInvestment)}
            </p>
          </div>
          <div className={`p-4 rounded-sm ${isDarkMode ? 'bg-neutral-light' : 'bg-neutral-lightest'}`}>
            <p className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>Total Profit</p>
            <p className={`text-2xl font-bold ${summaryData.totalProfit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {formatCurrency(summaryData.totalProfit)}
            </p>
          </div>
          <div className={`p-4 rounded-sm ${isDarkMode ? 'bg-neutral-light' : 'bg-neutral-lightest'}`}>
            <p className={`text-sm font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>Growth</p>
            <p className={`text-2xl font-bold ${summaryData.growthPercentage >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {(summaryData.growthPercentage || 0).toFixed(2)}%
            </p>
          </div>
        </div>
      </div>

      {/* NAV Data Table */}
      <NAVDataTable />
    </div>
  );
};

export default NAVTrackerDetailed;
