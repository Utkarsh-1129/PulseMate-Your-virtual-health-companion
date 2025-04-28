import axios from 'axios';

// Use import.meta.env for Vite
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "https://pulsemate-your-virtual-health-companion-1.onrender.com" || 'https://pulsemate-your-virtual-health-companion.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Send message to backend
export const sendMessage = (message, userId) => {
  return api.post('/chat', {
    message,
    user_id: userId
  });
};

// If you add more API calls later
export const getNearbyFacilities = (lat, lng, type) => {
  return api.get('/facilities', {
    params: { lat, lng, type }
  });
};

export default api;
