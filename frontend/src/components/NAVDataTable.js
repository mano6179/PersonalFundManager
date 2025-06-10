import React, { useEffect, useState } from 'react';
import { useTheme } from '../context/ThemeContext';

const NAVDataTable = () => {
  const { isDarkMode } = useTheme();
  const [navData, setNavData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchNAVData();
  }, []);

  const fetchNAVData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/nav/history');
      if (!response.ok) {
        throw new Error('Failed to fetch NAV data');
      }
      const data = await response.json();
      setNavData(data);
    } catch (err) {
      console.error('Error fetching NAV data:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Format currency
  const formatCurrency = (value) => {
    if (value === undefined || value === null) return '₹ -';
    return `₹ ${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className={`p-4 md:p-6 rounded-sm shadow-card ${isDarkMode ? 'bg-neutral-DEFAULT border border-neutral-light' : 'bg-white border border-neutral-lightest'}`}>
      <h3 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>NAV Data</h3>

      {/* Mobile view - simplified cards for each entry */}
      <div className="md:hidden space-y-4">
        {navData.map((row, index) => (
          <div
            key={index}
            className={`p-3 rounded-sm border ${
              isDarkMode
                ? 'border-neutral-light bg-neutral-DEFAULT'
                : 'border-neutral-lightest bg-white'
            }`}
          >
            <div className="flex justify-between items-center mb-2">
              <span className={`font-medium ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                {new Date(row.date).toLocaleDateString()}
              </span>
              <span className={`font-medium ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                NAV: {formatCurrency(row.nav_value)}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className={`block text-xs ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-light'}`}>Profit</span>
                <span className={isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}>
                  {formatCurrency(row.profit)}
                </span>
              </div>

              <div>
                <span className={`block text-xs ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-light'}`}>Charges</span>
                <span className={isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}>
                  {formatCurrency(row.charges)}
                </span>
              </div>

              <div>
                <span className={`block text-xs ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-light'}`}>Funds In/Out</span>
                <span className={isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}>
                  {formatCurrency(row.funds_in_out)}
                </span>
              </div>

              <div>
                <span className={`block text-xs ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-light'}`}>Previous NAV</span>
                <span className={isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}>
                  {formatCurrency(row.previous_nav)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Desktop view - full table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className={isDarkMode ? 'bg-neutral-light' : 'bg-neutral-lightest'}>
            <tr>
              <th scope="col" className={`px-3 py-3 text-left text-xs font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} uppercase tracking-wider`}>Date</th>
              <th scope="col" className={`px-3 py-3 text-right text-xs font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} uppercase tracking-wider`}>Profit</th>
              <th scope="col" className={`px-3 py-3 text-right text-xs font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} uppercase tracking-wider`}>Charges</th>
              <th scope="col" className={`px-3 py-3 text-right text-xs font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} uppercase tracking-wider`}>Funds In/Out</th>
              <th scope="col" className={`px-3 py-3 text-right text-xs font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} uppercase tracking-wider`}>Previous NAV</th>
              <th scope="col" className={`px-3 py-3 text-right text-xs font-medium ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} uppercase tracking-wider`}>NAV</th>
            </tr>
          </thead>
          <tbody className={`divide-y ${isDarkMode ? 'divide-neutral-light' : 'divide-neutral-lightest'}`}>
            {navData.map((row, index) => (
              <tr key={index} className={index % 2 === 0 ? (isDarkMode ? 'bg-neutral-DEFAULT' : 'bg-white') : (isDarkMode ? 'bg-neutral-light bg-opacity-30' : 'bg-neutral-lightest bg-opacity-50')}>
                <td className={`px-3 py-2 whitespace-nowrap text-sm ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
                  {new Date(row.date).toLocaleDateString()}
                </td>
                <td className={`px-3 py-2 whitespace-nowrap text-sm text-right ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
                  {formatCurrency(row.profit)}
                </td>
                <td className={`px-3 py-2 whitespace-nowrap text-sm text-right ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
                  {formatCurrency(row.charges)}
                </td>
                <td className={`px-3 py-2 whitespace-nowrap text-sm text-right ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
                  {formatCurrency(row.funds_in_out)}
                </td>
                <td className={`px-3 py-2 whitespace-nowrap text-sm text-right ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
                  {formatCurrency(row.previous_nav)}
                </td>
                <td className={`px-3 py-2 whitespace-nowrap text-sm text-right font-medium ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                  {formatCurrency(row.nav_value)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default NAVDataTable;
