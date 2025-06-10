import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import PublicLayout from './components/PublicLayout';
import LoggerForm from './pages/LoggerForm';
import WeeklyUpdatesList from './pages/WeeklyUpdatesList';
import MarketUpdates from './pages/MarketUpdates';
import PublicMarketUpdates from './pages/PublicMarketUpdates';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import NAVTrackerDetailed from './pages/NAVTrackerDetailed';
import TradeLog from './pages/TradeLog';
import Indicators from './pages/Indicators';
import EconomicCalendar from './pages/EconomicCalendar';
import ZerodhaPage from './pages/ZerodhaPage';
import ProtectedRoute from './components/ProtectedRoute';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import ZerodhaAuthSuccess from './pages/ZerodhaAuthSuccess';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />

            <Route path="/public/market-updates" element={
              <PublicLayout>
                <PublicMarketUpdates />
              </PublicLayout>
            } />

            {/* Protected routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/logger" element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <LoggerForm />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/weekly-updates" element={
              <ProtectedRoute>
                <Layout>
                  <WeeklyUpdatesList />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/nav-tracker-detailed" element={
              <ProtectedRoute>
                <Layout>
                  <NAVTrackerDetailed />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/trade-log" element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <TradeLog />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/indicators" element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <Indicators />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/economic-calendar" element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <EconomicCalendar />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/market-updates" element={
              <ProtectedRoute>
                <Layout>
                  <MarketUpdates />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/zerodha" element={
              <ProtectedRoute>
                <Layout>
                  <ZerodhaPage />
                </Layout>
              </ProtectedRoute>
            } />

            {/* Redirect any unknown routes */}
            <Route path="*" element={<Navigate to="/" replace />} />

            {/* Fallback for old login route */}
            <Route path="/login" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
