/** Author: Utkarsh Gupta, License: GPL v3 */

import { useState, useEffect } from 'react';
import { api } from '@/api/client';

export function useEngine() {
    const [backendStatus, setBackendStatus] = useState('connecting');

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const isHealthy = await api.health();
                if (isHealthy) {
                    setBackendStatus('online');
                } else {
                    setBackendStatus('offline');
                }
            } catch (err) {
                setBackendStatus('offline');
                console.log("Health Check Failed (Offline):", err);
            }
        };

        checkHealth();
        const interval = setInterval(checkHealth, 5000); // Check every 5s
        return () => clearInterval(interval);
    }, []);

    return { 
        status: backendStatus, 
        isOnline: backendStatus === 'online' 
    };
}
