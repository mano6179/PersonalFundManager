import { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useNAVData = () => {
    const [navData, setNavData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchNAVData = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`${API_URL}/api/nav/history`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch NAV data');
            }
            
            const data = await response.json();
            setNavData(data);
            setError(null);
        } catch (err) {
            console.error('NAV data fetch error:', err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchNAVData();
    }, []);

    return { navData, isLoading, error, refetch: fetchNAVData };
};