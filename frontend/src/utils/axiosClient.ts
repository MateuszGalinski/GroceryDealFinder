import axios from "axios";

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const refreshAccessToken = async () => {
  try {
    const response = await axiosClient.post("/auth/token/refresh/");
    const accessToken = response.data["access"];
    localStorage.setItem("accessToken", accessToken);
    return accessToken;
  } catch (error) {
    localStorage.clear();
    window.location.href = "/sign-in";
    throw new Error("Unable to refresh token");
  }
};

axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (originalRequest.url.includes("auth/")) {
      return Promise.reject(error);
    }

    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      try {
        const newToken = await refreshAccessToken();
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return axiosClient(originalRequest);
      } catch (err) {
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosClient;
