import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LogoutIcon from '@mui/icons-material/Logout';
import DashboardIcon from '@mui/icons-material/Dashboard';
import BarChartIcon from '@mui/icons-material/BarChart';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import SignalCellularAltIcon from '@mui/icons-material/SignalCellularAlt';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import AddIcon from '@mui/icons-material/Add';
import ArticleIcon from '@mui/icons-material/Article';
import ListAltIcon from '@mui/icons-material/ListAlt';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';

// Navigation items with roles
const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: <DashboardIcon fontSize="small" />, roles: ['admin', 'investor'] },
  { name: 'Trade Log', href: '/trade-log', icon: <BarChartIcon fontSize="small" />, roles: ['admin'] },
  { name: 'NAV', href: '/nav-tracker-detailed', icon: <ShowChartIcon fontSize="small" />, roles: ['admin', 'investor'] },
  { name: 'Indicators', href: '/indicators', icon: <SignalCellularAltIcon fontSize="small" />, roles: ['admin'] },
  { name: 'Economic Calendar', href: '/economic-calendar', icon: <CalendarMonthIcon fontSize="small" />, roles: ['admin'] },
  { name: 'Logger', href: '/logger', icon: <AddIcon fontSize="small" />, roles: ['admin'] },
  { name: 'Public Market Updates', href: '/public/market-updates', icon: <ArticleIcon fontSize="small" />, roles: ['admin', 'investor'] },
  { name: 'Activity Logs', href: '/weekly-updates', icon: <ListAltIcon fontSize="small" />, roles: ['admin'] },
  { name: 'Market Updates', href: '/market-updates', icon: <ArticleIcon fontSize="small" />, roles: ['admin', 'investor'] },
  { name: 'Zerodha', href: '/zerodha', icon: <AccountBalanceIcon fontSize="small" />, roles: ['admin', 'investor'] },
];

function Layout({ children }) {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const { currentUser, logout, isAdmin, isInvestor } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Close sidebar when screen size changes to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setSidebarOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Filter navigation items based on user role
  const filteredNavigation = navigation.filter(item => {
    if (!currentUser) return false;
    if (isAdmin()) return true;
    if (isInvestor() && item.roles.includes('investor')) return true;
    return false;
  });

  return (
    <div className={`flex h-screen ${isDarkMode ? 'bg-bgDark text-textLight' : 'bg-bgLight text-textDark'}`}>
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black bg-opacity-50 md:hidden"
          onClick={toggleSidebar}
        ></div>
      )}

      {/* Sidebar for mobile - slides in from left */}
      <div
        className={`fixed inset-y-0 left-0 z-30 w-64 transform transition-transform duration-300 ease-in-out md:hidden ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } ${isDarkMode ? 'bg-blue-900' : 'bg-blue-800'} text-white`}
      >
        {/* Close button for mobile */}
        <div className="absolute top-0 right-0 p-1 m-2">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-full text-white hover:bg-primary-light"
          >
            <CloseIcon fontSize="small" />
          </button>
        </div>

        {/* Logo area */}
        <div className="p-6 border-b border-opacity-20 border-white">
          <h1 className="text-xl font-bold tracking-tight text-white">Steady Gains</h1>
        </div>

        {/* Navigation */}
        <nav className="mt-6">
          {filteredNavigation.map((item) => {
            // Determine styling based on active route
            const isActive = location.pathname === item.href;
            const activeClasses = isActive
              ? `${isDarkMode ? 'bg-primary-light' : 'bg-primary-light'} border-l-4 border-accent-blue`
              : 'border-l-4 border-transparent';

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-6 py-3 ${activeClasses} hover:bg-primary-light transition-colors duration-200`}
                onClick={() => setSidebarOpen(false)} // Close sidebar on mobile when a link is clicked
              >
                <span className={`mr-3 ${isActive ? 'text-white' : 'text-white/80'}`}>
                  {item.icon}
                </span>
                <span className={`${isActive ? 'text-white font-medium' : 'text-white/80 font-normal'}`}>
                  {item.name}
                </span>
              </Link>
            );
          })}
        </nav>

        {/* Footer area */}
        <div className="absolute bottom-0 w-64 p-4 border-t border-opacity-20 border-white">
          <div className="text-xs text-white text-center">
            © 2025 Steady Gains
          </div>
        </div>
      </div>

      {/* Sidebar for desktop - always visible */}
      <div className={`hidden md:block w-64 ${isDarkMode ? 'bg-blue-900' : 'bg-blue-800'} text-white`}>
        {/* Logo area */}
        <div className="p-6 border-b border-opacity-20 border-white">
          <h1 className="text-xl font-bold tracking-tight text-white">Steady Gains</h1>
        </div>

        {/* Navigation */}
        <nav className="mt-6">
          {filteredNavigation.map((item) => {
            // Determine styling based on active route
            const isActive = location.pathname === item.href;
            const activeClasses = isActive
              ? `${isDarkMode ? 'bg-primary-light' : 'bg-primary-light'} border-l-4 border-accent-blue`
              : 'border-l-4 border-transparent';

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-6 py-3 ${activeClasses} hover:bg-primary-light transition-colors duration-200`}
              >
                <span className={`mr-3 ${isActive ? 'text-white' : 'text-white/80'}`}>
                  {item.icon}
                </span>
                <span className={`${isActive ? 'text-white font-medium' : 'text-white/80 font-normal'}`}>
                  {item.name}
                </span>
              </Link>
            );
          })}
        </nav>

        {/* Footer area */}
        <div className="absolute bottom-0 w-64 p-4 border-t border-opacity-20 border-white">
          <div className="text-xs text-white text-center">
            © 2025 Steady Gains
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden md:ml-0">
        {/* Header */}
        <header className={`${isDarkMode ? 'bg-bgDark' : 'bg-white'} border-b border-neutral-lightest shadow-sm z-10`}>
          <div className="flex justify-between items-center px-6 py-4">
            <div className="flex items-center">
              {/* Mobile menu button */}
              <button
                onClick={toggleSidebar}
                className={`md:hidden p-2 mr-3 rounded-md ${isDarkMode ? 'text-white hover:bg-primary-light' : 'text-primary-DEFAULT hover:bg-neutral-lightest'}`}
              >
                <MenuIcon />
              </button>
              <h2 className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                {filteredNavigation.find(item => item.href === location.pathname)?.name || 'Dashboard'}
              </h2>
            </div>
            <div className="flex items-center space-x-3 md:space-x-6">
              <button
                onClick={toggleDarkMode}
                className={`p-1 rounded-full ${isDarkMode ? 'text-neutral-lighter hover:text-white' : 'text-neutral-light hover:text-primary-DEFAULT'}`}
              >
                {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
              </button>
              <div className="flex items-center">
                <div className={`h-8 w-8 rounded-full bg-primary-light ${isDarkMode ? 'text-white' : 'text-black'} flex items-center justify-center mr-2 text-sm font-medium`}>
                  {currentUser?.name?.charAt(0) || 'U'}
                </div>
                <div className={`hidden sm:block font-medium ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>{currentUser?.name}</div>
              </div>
              <button
                onClick={handleLogout}
                className={`p-1 rounded-full ${isDarkMode ? 'text-neutral-lighter hover:text-white' : 'text-neutral-light hover:text-primary-DEFAULT'}`}
              >
                <LogoutIcon />
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className={`flex-1 overflow-auto p-4 md:p-6 ${isDarkMode ? 'bg-bgDark' : 'bg-neutral-lightest'}`}>
          {children}
        </main>
      </div>
    </div>
  );
}

export default Layout;

// These components are moved to FormElements.js
