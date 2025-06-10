import { useState, useEffect } from 'react';

export const useNAVData = () => {
    const [navData, setNavData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchNAVData = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/nav/history');
            
            if (!response.ok) {
                throw new Error(`Failed to fetch NAV data: ${response.statusText}`);
            }
            
            const data = await response.json();
            setNavData(data);
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