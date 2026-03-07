const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://kmapeee.onrender.com";

export const API_BASE_URL = RAW_API_BASE_URL.replace(/\/+$/, "");

export const apiUrl = (path) => `${API_BASE_URL}${path}`;
