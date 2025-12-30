const API_URL = import.meta.env.VITE_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://design-red-pen-mentor.onrender.com');
export const STRIPE_PAYMENT_LINK = "https://buy.stripe.com/14AdR8bgv5X15C90eeaAw03"; // Standard Plan (Web)

export default API_URL;
