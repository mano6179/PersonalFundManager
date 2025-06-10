import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { useTheme } from '../context/ThemeContext';
import { useNAVData } from '../hooks/useNAVData';

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const NAVGraph = () => {
  const { isDarkMode } = useTheme();
  const { navData, isLoading, error } = useNAVData();

  if (isLoading) {
    return (
      <div className={`p-4 rounded-sm shadow-card ${isDarkMode ? 'bg-neutral-DEFAULT border border-neutral-light' : 'bg-white border border-neutral-lightest'}`}>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-DEFAULT mx-auto"></div>
          <p className={`mt-2 ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>Loading NAV chart...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 rounded-sm shadow-card ${isDarkMode ? 'bg-neutral-DEFAULT border border-neutral-light' : 'bg-white border border-neutral-lightest'}`}>
        <div className="text-center py-8">
          <p className={`text-accent-red ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>Error loading chart: {error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-primary-DEFAULT text-white rounded-sm hover:bg-primary-dark transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!navData || navData.length === 0) {
    return (
      <div className={`p-4 rounded-sm shadow-card ${isDarkMode ? 'bg-neutral-DEFAULT border border-neutral-light' : 'bg-white border border-neutral-lightest'}`}>
        <div className="text-center py-8">
          <p className={`${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>No NAV data available</p>
        </div>
      </div>
    );
  }

  const chartData = {
    labels: navData.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [{
      label: 'NAV Value',
      data: navData.map(item => item.nav_value),
      borderColor: isDarkMode ? 'rgb(134, 239, 172)' : 'rgb(34, 197, 94)',
      backgroundColor: isDarkMode ? 'rgba(134, 239, 172, 0.1)' : 'rgba(34, 197, 94, 0.1)',
      tension: 0.1,
      fill: true
    }]
  };

  return (
    <div className={`p-4 rounded-sm shadow-card ${isDarkMode ? 'bg-neutral-DEFAULT border border-neutral-light' : 'bg-white border border-neutral-lightest'}`}>
      <h3 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>NAV Trend</h3>
      <div className="h-96">
        <Line data={chartData} options={{
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: false,
              grid: {
                color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
              },
              ticks: {
                callback: function(value) {
                  return '₹' + value.toLocaleString();
                }
              }
            },
            x: {
              grid: {
                color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
              }
            }
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `NAV: ₹${context.parsed.y.toLocaleString()}`;
                }
              }
            }
          }
        }} />
      </div>
    </div>
  );
};

export default NAVGraph;