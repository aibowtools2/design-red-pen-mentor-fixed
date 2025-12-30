const API_URL = import.meta.env.VITE_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://design-red-pen-mentor.onrender.com');

export default API_URL;
