import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import LoginIcon from '@mui/icons-material/Login';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import CloseIcon from '@mui/icons-material/Close';
import PersonIcon from '@mui/icons-material/Person';
import LockIcon from '@mui/icons-material/Lock';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import BarChartIcon from '@mui/icons-material/BarChart';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const LandingPage = () => {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [marketUpdates, setMarketUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [loginSliderOpen, setLoginSliderOpen] = useState(false);

  // Refs for scrolling to sections
  const aboutRef = useRef(null);
  const aspirationsRef = useRef(null);
  const marketUpdatesRef = useRef(null);
  const contactRef = useRef(null);

  // Login form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState('');

  // Format timestamp to readable date
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Scroll to section function
  const scrollToSection = (ref) => {
    if (ref && ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Handle login form submission
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginLoading(true);
    setLoginError('');

    try {
      await login(email, password);
      setLoginSliderOpen(false);
      navigate('/dashboard');
    } catch (error) {
      setLoginError('Invalid email or password. Please try again.');
      console.error('Login error:', error);
    } finally {
      setLoginLoading(false);
    }
  };

  useEffect(() => {
    // Initialize localStorage with mock data if it doesn't exist
    initializeMarketUpdates();
    fetchMarketUpdates();
  }, []);

  const initializeMarketUpdates = () => {
    // Check if data already exists in localStorage
    const storedLogsJSON = localStorage.getItem('steadyGainsLogs');

    if (!storedLogsJSON) {
      // If no data exists, initialize with mock data
      const mockUpdates = [
        {
          id: 1,
          type: 'market_update',
          timestamp: '2025-05-05T22:42:00',
          title: 'Caution creeping in?',
          content: 'Markets saw muted movement today with NIFTY forming a small-bodied candle. The index closed at 24,850, up just 0.2%. Bank NIFTY underperformed, closing down 0.3% at 52,340.\n\nThe market breadth was negative with decliners outnumbering advancers. The India VIX rose 4% to 14.5, indicating some nervousness.\n\nFIIs were net sellers to the tune of ₹1,200 crores while DIIs bought ₹950 crores worth of equities.\n\nGlobal cues are mixed with US futures pointing slightly lower and Asian markets trading flat. Crude oil is stable at $82 per barrel.\n\nThe market seems to be taking a breather after the recent rally. Key levels to watch: NIFTY support at 24,600 and resistance at 25,000.'
        },
        {
          id: 2,
          type: 'market_update',
          timestamp: '2025-05-02T23:07:00',
          title: 'Volatility brewing?',
          content: 'NIFTY ended flat after swinging both sides. The index closed at 24,800, unchanged from yesterday. Bank NIFTY showed strength, closing up 0.5% at 52,500.\n\nThe market breadth was positive with advancers outnumbering decliners. The India VIX dropped 2% to 13.9, indicating reduced fear.\n\nFIIs were net buyers to the tune of ₹850 crores while DIIs sold ₹650 crores worth of equities.\n\nGlobal cues are positive with US markets closing higher and Asian markets trading in the green. Crude oil is down 1% at $81 per barrel.\n\nThe market seems to be consolidating in a range. Key levels to watch: NIFTY support at 24,600 and resistance at 25,000.'
        },
        {
          id: 3,
          type: 'market_update',
          timestamp: '2025-05-01T22:23:00',
          title: 'Profit booking or pause?',
          content: 'Markets saw some profit booking today with NIFTY closing down 0.3% at 24,800. Bank NIFTY also closed lower by 0.4% at 52,250.\n\nThe market breadth was negative with decliners outnumbering advancers. The India VIX rose 3% to 14.2, indicating some nervousness.\n\nFIIs were net sellers to the tune of ₹950 crores while DIIs bought ₹750 crores worth of equities.\n\nGlobal cues are mixed with US futures pointing slightly lower and Asian markets trading flat. Crude oil is stable at $82 per barrel.\n\nThe market seems to be taking a breather after the recent rally. Key levels to watch: NIFTY support at 24,600 and resistance at 25,000.'
        }
      ];

      // Save to localStorage
      localStorage.setItem('steadyGainsLogs', JSON.stringify(mockUpdates));
    }
  };

  const fetchMarketUpdates = async () => {
    try {
      setLoading(true);

      // Get logs from localStorage
      const storedLogsJSON = localStorage.getItem('steadyGainsLogs');

      if (storedLogsJSON) {
        const allLogs = JSON.parse(storedLogsJSON);

        // Filter to get only market_update logs and sort by timestamp (newest first)
        const updates = allLogs
          .filter(log => log.type === 'market_update')
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        setMarketUpdates(updates);
        setError(null);
      } else {
        // If no logs in localStorage, use mock data
        const mockUpdates = [
          {
            id: 1,
            type: 'market_update',
            timestamp: '2025-05-05T22:42:00',
            title: 'Caution creeping in?',
            content: 'Markets saw muted movement today with NIFTY forming a small-bodied candle. The index closed at 24,850, up just 0.2%. Bank NIFTY underperformed, closing down 0.3% at 52,340.\n\nThe market breadth was negative with decliners outnumbering advancers. The India VIX rose 4% to 14.5, indicating some nervousness.\n\nFIIs were net sellers to the tune of ₹1,200 crores while DIIs bought ₹950 crores worth of equities.\n\nGlobal cues are mixed with US futures pointing slightly lower and Asian markets trading flat. Crude oil is stable at $82 per barrel.\n\nThe market seems to be taking a breather after the recent rally. Key levels to watch: NIFTY support at 24,600 and resistance at 25,000.'
          },
          {
            id: 2,
            type: 'market_update',
            timestamp: '2025-05-02T23:07:00',
            title: 'Volatility brewing?',
            content: 'NIFTY ended flat after swinging both sides. The index closed at 24,800, unchanged from yesterday. Bank NIFTY showed strength, closing up 0.5% at 52,500.\n\nThe market breadth was positive with advancers outnumbering decliners. The India VIX dropped 2% to 13.9, indicating reduced fear.\n\nFIIs were net buyers to the tune of ₹850 crores while DIIs sold ₹650 crores worth of equities.\n\nGlobal cues are positive with US markets closing higher and Asian markets trading in the green. Crude oil is down 1% at $81 per barrel.\n\nThe market seems to be consolidating in a range. Key levels to watch: NIFTY support at 24,600 and resistance at 25,000.'
          },
          {
            id: 3,
            type: 'market_update',
            timestamp: '2025-05-01T22:23:00',
            title: 'Profit booking or pause?',
            content: 'Markets saw some profit booking today with NIFTY closing down 0.3% at 24,800. Bank NIFTY also closed lower by 0.4% at 52,250.\n\nThe market breadth was negative with decliners outnumbering advancers. The India VIX rose 3% to 14.2, indicating some nervousness.\n\nFIIs were net sellers to the tune of ₹950 crores while DIIs bought ₹750 crores worth of equities.\n\nGlobal cues are mixed with US futures pointing slightly lower and Asian markets trading flat. Crude oil is stable at $82 per barrel.\n\nThe market seems to be taking a breather after the recent rally. Key levels to watch: NIFTY support at 24,600 and resistance at 25,000.'
          }
        ];

        setMarketUpdates(mockUpdates);
      }
    } catch (err) {
      console.error('Error fetching market updates:', err);
      setError('Failed to load market updates. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-800'}`}>
      {/* Navigation Bar */}
      <nav className={`sticky top-0 z-40 ${isDarkMode ? 'bg-blue-900' : 'bg-blue-800'} shadow-md`}>
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/" className="text-white text-xl font-bold">
                Steady Gains
              </Link>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-4">
              <button
                onClick={() => scrollToSection(aboutRef)}
                className="text-white hover:text-blue-200 transition-colors duration-200"
              >
                About
              </button>
              <button
                onClick={() => scrollToSection(aspirationsRef)}
                className="text-white hover:text-blue-200 transition-colors duration-200"
              >
                Aspirations
              </button>
              <button
                onClick={() => scrollToSection(marketUpdatesRef)}
                className="text-white hover:text-blue-200 transition-colors duration-200"
              >
                Market Updates
              </button>
              <button
                onClick={() => scrollToSection(contactRef)}
                className="text-white hover:text-blue-200 transition-colors duration-200"
              >
                Contact Us
              </button>
            </div>

            {/* Dark Mode Toggle and Login Button */}
            <div className="flex items-center space-x-4">
              {/* Dark Mode Toggle */}
              <button
                onClick={toggleDarkMode}
                className={`p-2 rounded-full ${
                  isDarkMode
                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                    : 'bg-blue-500 text-black hover:bg-blue-600'
                } transition-colors duration-200`}
                aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDarkMode ? <LightModeIcon /> : <DarkModeIcon />}
              </button>

              {/* Login Button */}
              <button
                onClick={() => setLoginSliderOpen(true)}
                className="flex items-center px-4 py-2 rounded-sm bg-white text-blue-800 hover:bg-gray-100 transition-colors duration-200"
              >
                <LoginIcon className="mr-2" />
                <span>Login</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className={`py-16 px-4 ${isDarkMode ? 'bg-primary-dark' : 'bg-primary-DEFAULT'}`}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <h1 className={`text-4xl md:text-5xl font-bold mb-6 ${isDarkMode ? 'text-white' : 'text-black'}`}>
              Welcome to Steady Gains
            </h1>
            <p className={`text-xl mb-8 max-w-3xl mx-auto ${isDarkMode ? 'text-white/90' : 'text-black'}`}>
              A disciplined approach to trading with consistent returns and risk management
            </p>

            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button
                onClick={() => document.getElementById('market-updates').scrollIntoView({ behavior: 'smooth' })}
                className={`flex items-center justify-center px-6 py-3 rounded-md ${
                  isDarkMode
                    ? 'bg-accent-blue text-white hover:bg-accent-blue/80'
                    : 'bg-accent-blue text-white hover:bg-accent-blue/80'
                } transition-colors duration-200`}
              >
                Market Updates
              </button>
              <Link
                to="/public/market-updates"
                className={`flex items-center justify-center px-6 py-3 rounded-md ${
                  isDarkMode
                    ? 'bg-transparent border border-white text-white hover:bg-white/10'
                    : 'bg-transparent border border-black text-black hover:bg-black/10'
                } transition-colors duration-200`}
              >
                View All Updates
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* About Fund Section */}
      <section id="about" ref={aboutRef} className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className={`text-3xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
              About Our Fund
            </h2>
            <div className="w-20 h-1 bg-accent-blue mx-auto"></div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className={`p-6 rounded-lg ${isDarkMode ? 'bg-neutral-DEFAULT' : 'bg-white'} shadow-md`}>
              <div className="flex justify-center mb-4">
                <div className={`p-3 rounded-full ${isDarkMode ? 'bg-primary-DEFAULT' : 'bg-primary-light'}`}>
                  <BarChartIcon className="text-white text-3xl" />
                </div>
              </div>
              <h3 className={`text-xl font-semibold mb-3 text-center ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                Disciplined Approach
              </h3>
              <p className={`text-center ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}`}>
                Our trading strategy is built on strict discipline, with clear entry and exit rules that remove emotional decision-making from the process.
              </p>
            </div>

            <div className={`p-6 rounded-lg ${isDarkMode ? 'bg-neutral-DEFAULT' : 'bg-white'} shadow-md`}>
              <div className="flex justify-center mb-4">
                <div className={`p-3 rounded-full ${isDarkMode ? 'bg-primary-DEFAULT' : 'bg-primary-light'}`}>
                  <ShowChartIcon className="text-white text-3xl" />
                </div>
              </div>
              <h3 className={`text-xl font-semibold mb-3 text-center ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                Risk Management
              </h3>
              <p className={`text-center ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}`}>
                Capital preservation is our priority. We employ sophisticated risk management techniques to protect investments during market downturns.
              </p>
            </div>

            <div className={`p-6 rounded-lg ${isDarkMode ? 'bg-neutral-DEFAULT' : 'bg-white'} shadow-md`}>
              <div className="flex justify-center mb-4">
                <div className={`p-3 rounded-full ${isDarkMode ? 'bg-primary-DEFAULT' : 'bg-primary-light'}`}>
                  <TrendingUpIcon className="text-white text-3xl" />
                </div>
              </div>
              <h3 className={`text-xl font-semibold mb-3 text-center ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                Consistent Returns
              </h3>
              <p className={`text-center ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}`}>
                Our goal is to deliver steady, consistent returns over time rather than chasing high-risk opportunities with unpredictable outcomes.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Fund Aspirations */}
      <section id="aspirations" ref={aspirationsRef} className={`py-16 px-4 ${isDarkMode ? 'bg-neutral-dark' : 'bg-neutral-lightest'}`}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className={`text-3xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
              Our Aspirations
            </h2>
            <div className="w-20 h-1 bg-accent-blue mx-auto"></div>
          </div>

          <div className={`p-8 rounded-lg ${isDarkMode ? 'bg-neutral-DEFAULT' : 'bg-white'} shadow-md`}>
            <p className={`text-lg mb-6 ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
              At Steady Gains, we aspire to:
            </p>
            <ul className="space-y-4">
              <li className="flex items-start">
                <span className={`mr-3 mt-1 ${isDarkMode ? 'text-accent-blue' : 'text-accent-blue'}`}>
                  <ArrowForwardIcon />
                </span>
                <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                  <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Outperform market indices</strong> - We aim to consistently deliver returns that exceed major market benchmarks while maintaining lower volatility.
                </p>
              </li>
              <li className="flex items-start">
                <span className={`mr-3 mt-1 ${isDarkMode ? 'text-accent-blue' : 'text-accent-blue'}`}>
                  <ArrowForwardIcon />
                </span>
                <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                  <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Provide transparency</strong> - We believe in complete transparency with our investors, sharing detailed insights into our trading strategies and performance.
                </p>
              </li>
              <li className="flex items-start">
                <span className={`mr-3 mt-1 ${isDarkMode ? 'text-accent-blue' : 'text-accent-blue'}`}>
                  <ArrowForwardIcon />
                </span>
                <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                  <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Educate our investors</strong> - Beyond managing investments, we aim to help our investors understand market dynamics through regular updates and insights.
                </p>
              </li>
              <li className="flex items-start">
                <span className={`mr-3 mt-1 ${isDarkMode ? 'text-accent-blue' : 'text-accent-blue'}`}>
                  <ArrowForwardIcon />
                </span>
                <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                  <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Scale with discipline</strong> - As we grow, we remain committed to our core principles of disciplined trading and risk management.
                </p>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Market Updates Section */}
      <section id="market-updates" ref={marketUpdatesRef} className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className={`text-3xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
              Market Updates
            </h2>
            <div className="w-20 h-1 bg-accent-blue mx-auto mb-4"></div>
            <p className={`max-w-3xl mx-auto ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}`}>
              Stay informed with our latest market insights and analysis
            </p>
          </div>

          {loading ? (
            <div className={`text-center py-4 ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
              Loading market updates...
            </div>
          ) : error ? (
            <div className={`text-center py-4 ${isDarkMode ? 'text-accent-red' : 'text-accent-red'}`}>
              {error}
            </div>
          ) : marketUpdates.length === 0 ? (
            <div className={`text-center py-4 ${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'}`}>
              No market updates available.
            </div>
          ) : (
            <div className="space-y-8">
              {/* Featured Latest Update */}
              {marketUpdates.length > 0 && (
                <div className={`p-8 rounded-lg border-2 ${
                  isDarkMode
                    ? 'border-accent-blue bg-neutral-DEFAULT'
                    : 'border-accent-blue bg-white'
                } shadow-lg`}>
                  <div className="flex items-center mb-2">
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                      isDarkMode ? 'bg-accent-blue text-white' : 'bg-accent-blue/20 text-accent-blue'
                    } mr-2`}>
                      Latest Update
                    </span>
                    <span className={`text-sm ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-light'}`}>
                      {formatTimestamp(marketUpdates[0].timestamp)}
                    </span>
                  </div>

                  <h3 className={`text-2xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                    {marketUpdates[0].title}
                  </h3>

                  <div className={`${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} whitespace-pre-line mb-6`}>
                    <p className="text-lg">
                      {marketUpdates[0].content.split('\n\n')[0]}
                    </p>

                    {marketUpdates[0].content.split('\n\n').length > 1 && (
                      <div className="mt-4">
                        <p>
                          {marketUpdates[0].content.split('\n\n')[1]}
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="flex justify-end">
                    <Link
                      to="/public/market-updates"
                      className={`inline-flex items-center px-4 py-2 rounded-md ${
                        isDarkMode
                          ? 'bg-accent-blue text-white hover:bg-accent-blue/80'
                          : 'bg-accent-blue text-white hover:bg-accent-blue/80'
                      } transition-colors duration-200`}
                    >
                      Read Full Update <ArrowForwardIcon className="ml-1" fontSize="small" />
                    </Link>
                  </div>
                </div>
              )}

              {/* Recent Updates */}
              <h3 className={`text-xl font-semibold mt-12 mb-6 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                Recent Updates
              </h3>

              {marketUpdates.slice(1, 3).map((update) => (
                <div
                  key={update.id}
                  className={`p-6 rounded-lg border ${
                    isDarkMode
                      ? 'border-neutral-light bg-neutral-DEFAULT'
                      : 'border-neutral-lightest bg-white'
                  } shadow-md`}
                >
                  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4">
                    <h3 className={`text-xl font-semibold ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                      {update.title}
                    </h3>
                    <span className={`text-sm mt-1 sm:mt-0 ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-light'}`}>
                      {formatTimestamp(update.timestamp)}
                    </span>
                  </div>
                  <p className={`${isDarkMode ? 'text-white' : 'text-neutral-DEFAULT'} whitespace-pre-line mb-4`}>
                    {update.content.length > 300
                      ? `${update.content.substring(0, 300)}...`
                      : update.content}
                  </p>
                  {update.content.length > 300 && (
                    <div className="text-right">
                      <Link
                        to="/public/market-updates"
                        className={`inline-flex items-center ${isDarkMode ? 'text-accent-blue hover:text-accent-blue/80' : 'text-accent-blue hover:text-accent-blue/80'}`}
                      >
                        Read more <ArrowForwardIcon className="ml-1" fontSize="small" />
                      </Link>
                    </div>
                  )}
                </div>
              ))}

              <div className="text-center mt-8">
                <Link
                  to="/public/market-updates"
                  className={`inline-flex items-center justify-center px-6 py-3 rounded-md ${
                    isDarkMode
                      ? 'bg-primary-DEFAULT text-white hover:bg-primary-light'
                      : 'bg-primary-DEFAULT text-black hover:bg-primary-light'
                  } transition-colors duration-200`}
                >
                  View All Market Updates <ArrowForwardIcon className="ml-2" fontSize="small" />
                </Link>
              </div>
            </div>
          )}
        </div>
      </section>
      {/* Contact Section */}
      <section id="contact" ref={contactRef} className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className={`text-3xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
              Contact Us
            </h2>
            <div className="w-20 h-1 bg-accent-blue mx-auto mb-6"></div>
            <p className={`max-w-3xl mx-auto ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}`}>
              Have questions about our fund or interested in investing? Get in touch with our team.
            </p>
          </div>

          <div className={`max-w-3xl mx-auto p-8 rounded-lg ${isDarkMode ? 'bg-neutral-DEFAULT' : 'bg-white'} shadow-md`}>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                  Contact Information
                </h3>
                <div className="space-y-4">
                  <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                    <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Email:</strong> info@steadygains.com
                  </p>
                  <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                    <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Phone:</strong> +91 123 456 7890
                  </p>
                  <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                    <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Address:</strong> 123 Financial District, Mumbai, India
                  </p>
                </div>
              </div>

              <div>
                <h3 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                  Business Hours
                </h3>
                <div className="space-y-4">
                  <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                    <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Monday - Friday:</strong> 9:00 AM - 5:00 PM
                  </p>
                  <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                    <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Saturday:</strong> 10:00 AM - 2:00 PM
                  </p>
                  <p className={isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}>
                    <strong className={isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}>Sunday:</strong> Closed
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={`py-8 px-4 ${isDarkMode ? 'bg-blue-900' : 'bg-blue-800'} text-white shadow-md`}>
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Steady Gains</h3>
              <p className="text-sm text-white/80">
                A disciplined approach to trading with consistent returns and risk management.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li><button onClick={() => scrollToSection('about')} className="text-white/80 hover:text-white transition-colors duration-200">About</button></li>
                <li><button onClick={() => scrollToSection('aspirations')} className="text-white/80 hover:text-white transition-colors duration-200">Aspirations</button></li>
                <li><button onClick={() => scrollToSection('market-updates')} className="text-white/80 hover:text-white transition-colors duration-200">Market Updates</button></li>
                <li><button onClick={() => scrollToSection('contact')} className="text-white/80 hover:text-white transition-colors duration-200">Contact</button></li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li><button className="text-white/80 hover:text-white transition-colors duration-200">Privacy Policy</button></li>
                <li><button className="text-white/80 hover:text-white transition-colors duration-200">Terms of Service</button></li>
                <li><button className="text-white/80 hover:text-white transition-colors duration-200">Disclaimer</button></li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Connect</h3>
              <div className="flex space-x-4">
                <button className="text-white/80 hover:text-white transition-colors duration-200" aria-label="Facebook">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fillRule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clipRule="evenodd" />
                  </svg>
                </button>
                <button className="text-white/80 hover:text-white transition-colors duration-200" aria-label="Twitter">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </button>
                <button className="text-white/80 hover:text-white transition-colors duration-200" aria-label="Instagram">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fillRule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clipRule="evenodd" />
                  </svg>
                </button>
                <button className="text-white/80 hover:text-white transition-colors duration-200" aria-label="GitHub">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-white/20 text-center">
            <p className="text-sm text-white/60">
              © {new Date().getFullYear()} Steady Gains. All rights reserved.
            </p>
          </div>
        </div>
      </footer>

      {/* Login Slider */}
      {loginSliderOpen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-75 flex justify-end">
          <div
            className={`w-full max-w-md h-full ${
              isDarkMode ? 'bg-neutral-DEFAULT' : 'bg-white'
            } p-6 overflow-y-auto`}
          >
            <div className="flex justify-between items-center mb-8">
              <h2 className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-primary-DEFAULT'}`}>
                Login to Your Account
              </h2>
              <button
                onClick={() => setLoginSliderOpen(false)}
                className={`p-2 rounded-full ${isDarkMode ? 'text-white hover:bg-neutral-light' : 'text-neutral-DEFAULT hover:bg-neutral-lightest'}`}
              >
                <CloseIcon />
              </button>
            </div>

            {loginError && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {loginError}
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label
                  htmlFor="email"
                  className={`block text-sm font-medium ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'} mb-1`}
                >
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <PersonIcon className={`h-5 w-5 ${isDarkMode ? 'text-neutral-light' : 'text-neutral-light'}`} />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={`block w-full pl-10 pr-3 py-2 border ${
                      isDarkMode
                        ? 'bg-white border-neutral-light text-black'
                        : 'bg-white border-neutral-light text-neutral-DEFAULT'
                    } rounded-md focus:outline-none focus:ring-2 focus:ring-accent-blue focus:border-transparent`}
                    placeholder="you@example.com"
                  />
                </div>
              </div>

              <div>
                <label
                  htmlFor="password"
                  className={`block text-sm font-medium ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'} mb-1`}
                >
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <LockIcon className={`h-5 w-5 ${isDarkMode ? 'text-neutral-light' : 'text-neutral-light'}`} />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className={`block w-full pl-10 pr-10 py-2 border ${
                      isDarkMode
                        ? 'bg-white border-neutral-light text-black'
                        : 'bg-white border-neutral-light text-neutral-DEFAULT'
                    } rounded-md focus:outline-none focus:ring-2 focus:ring-accent-blue focus:border-transparent`}
                    placeholder="••••••••"
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className={`${isDarkMode ? 'text-neutral-light hover:text-white' : 'text-neutral-light hover:text-neutral-DEFAULT'}`}
                    >
                      {showPassword ? <VisibilityOffIcon className="h-5 w-5" /> : <VisibilityIcon className="h-5 w-5" />}
                    </button>
                  </div>
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loginLoading}
                  className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                    loginLoading
                      ? 'bg-accent-blue/70 cursor-not-allowed'
                      : 'bg-accent-blue hover:bg-accent-blue/90'
                  } transition-colors duration-200`}
                >
                  {loginLoading ? 'Logging in...' : 'Login'}
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className={`h-4 w-4 ${
                      isDarkMode
                        ? 'bg-neutral-dark border-neutral-light text-accent-blue'
                        : 'bg-white border-neutral-light text-accent-blue'
                    } rounded focus:ring-accent-blue`}
                  />
                  <label
                    htmlFor="remember-me"
                    className={`ml-2 block text-sm ${isDarkMode ? 'text-neutral-lighter' : 'text-neutral-DEFAULT'}`}
                  >
                    Remember me
                  </label>
                </div>

                <div className="text-sm">
                  <button
                    className={`font-medium ${isDarkMode ? 'text-accent-blue hover:text-accent-blue/80' : 'text-accent-blue hover:text-accent-blue/80'}`}
                  >
                    Forgot password?
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;








