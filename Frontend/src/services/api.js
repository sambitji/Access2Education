// =============================================================
// frontend/src/services/api.js
// Edu-Platform — Axios Instance
//
// Kya karta hai:
//   - Backend ke liye configured axios instance
//   - Har request mein Authorization header auto-add
//   - 401 error pe refresh token se naya access token lo
//   - Refresh fail hone pe logout kar do
// =============================================================

import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ── Axios Instance ────────────────────────────────────────────
const api = axios.create({
  baseURL:        BASE_URL,
  timeout:        10000,
  headers: { "Content-Type": "application/json" },
});


// ── Request Interceptor — Token attach karo ──────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);


// ── Response Interceptor — 401 pe refresh karo ───────────────
let isRefreshing   = false;
let failedRequests = [];

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;

    // 401 aaya aur ye already retry nahi hai
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        // Queue mein add karo — refresh chal raha hai
        return new Promise((resolve, reject) => {
          failedRequests.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;
      const refreshToken = localStorage.getItem("refresh_token");

      if (!refreshToken) {
        // Refresh token nahi hai — logout karo
        _forceLogout();
        return Promise.reject(error);
      }

      try {
        const res = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const newToken = res.data.access_token;
        localStorage.setItem("access_token", newToken);

        // Queue ke saare requests retry karo
        failedRequests.forEach((req) => req.resolve(newToken));
        failedRequests = [];

        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);

      } catch (refreshError) {
        // Refresh bhi fail — logout
        failedRequests.forEach((req) => req.reject(refreshError));
        failedRequests = [];
        _forceLogout();
        return Promise.reject(refreshError);

      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

function _forceLogout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

export default api;