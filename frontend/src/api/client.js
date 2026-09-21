import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'synchrony-hackathon-2024';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  },
});

export const assessApplicant = (data) => client.post('/assess', data);
export const getMetrics = () => client.get('/metrics');
export const submitOverride = (data) => client.post('/override', data);
export const getHealth = () => client.get('/health');

export default client;
