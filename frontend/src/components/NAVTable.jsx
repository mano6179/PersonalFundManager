import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { useNAVData } from '../hooks/useNAVData';

const NAVTable = () => {
  const { isDarkMode } = useTheme();
  const { navData, isLoading, error } = useNAVData();

  if (isLoading) return <div>Loading table...</div>;
  if (error) return <div>Error loading table: {error}</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className={isDarkMode ? 'bg-gray-800' : 'bg-gray-50'}>
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Date</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">NAV Value</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Change</th>
          </tr>
        </thead>
        <tbody className={isDarkMode ? 'bg-gray-900' : 'bg-white'}>
          {navData.map((item, index) => {
            const prevNAV = index > 0 ? navData[index - 1].nav_value : item.nav_value;
            const change = ((item.nav_value - prevNAV) / prevNAV) * 100;
            
            return (
              <tr key={item._id || index}>
                <td className="px-6 py-4">{new Date(item.date).toLocaleDateString()}</td>
                <td className="px-6 py-4">₹{item.nav_value.toFixed(2)}</td>
                <td className={`px-6 py-4 ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {change.toFixed(2)}%
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default NAVTable;