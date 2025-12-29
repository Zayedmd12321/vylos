import axios from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
});

// Add a request interceptor to include the token in future requests
api.interceptors.request.use((config) => {
  const token = Cookies.get("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const loginWithProvider = async (provider: "github" | "google") => {
  const { data } = await api.get(`/login/${provider}`);
  window.location.href = data.url;
};

export default api;