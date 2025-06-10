import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to add the auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add a response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If the error is 401 and we haven't tried to refresh the token yet
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
                const { access_token, refresh_token } = response.data;

                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);

                // Retry the original request with the new token
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                return api(originalRequest);
            } catch (refreshError) {
                // If refresh token fails, logout the user
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    login: (credentials) => api.post('/auth/login', credentials),
    register: (userData) => api.post('/auth/register', userData),
    logout: () => api.post('/auth/logout'),
    getCurrentUser: () => api.get('/auth/me'),
};

// Market Updates API
export const marketUpdatesAPI = {
    getUpdates: (params) => api.get('/market-updates', { params }),
    getPublicUpdates: (params) => api.get('/market-updates/public', { params }),
    getUpdate: (id) => api.get(`/market-updates/${id}`),
    createUpdate: (data) => api.post('/market-updates', data),
    updateUpdate: (id, data) => api.put(`/market-updates/${id}`, data),
    deleteUpdate: (id) => api.delete(`/market-updates/${id}`),
    searchUpdates: (query, params) => api.get('/market-updates/search', { 
        params: { query, ...params } 
    }),
};

// Trade Logs API
export const tradeLogsAPI = {
    getLogs: (params) => api.get('/trade-logs', { params }),
    getLog: (id) => api.get(`/trade-logs/${id}`),
    createLog: (data) => api.post('/trade-logs', data),
    updateLog: (id, data) => api.put(`/trade-logs/${id}`, data),
    deleteLog: (id) => api.delete(`/trade-logs/${id}`),
};

// User Preferences API
export const userPreferencesAPI = {
    getPreferences: () => api.get('/users/preferences'),
    updatePreferences: (data) => api.put('/users/preferences', data),
};

export default api; 