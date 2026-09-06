import axios from "axios";

const client = axios.create({
   baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

client.interceptors.request.use((config) => {
   const token = localStorage.getItem("creditpulse_token");
   if (token) config.headers.Authorization = `Bearer ${token}`;
   return config;
});

client.interceptors.response.use(
   (response) => response,
   (error) => {
      if (error.response?.status === 401) {
         localStorage.removeItem("creditpulse_token");
         window.location.assign("/login");
      }
      return Promise.reject(error);
   },
);

export default client;
