import { create } from "zustand";

const STORAGE_KEYS = {
  user: "edu_platform_user",
  accessToken: "access_token",
  refreshToken: "refresh_token",
};

const useAuthStore = create((set) => ({
  user: null,
  isLoading: true,

  initAuth: () => {
    try {
      const savedUser = JSON.parse(localStorage.getItem(STORAGE_KEYS.user));
      set({ user: savedUser || null, isLoading: false });
    } catch (err) {
      set({ user: null, isLoading: false });
    }
  },

  login: (user, accessToken, refreshToken) => {
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user));
    localStorage.setItem(STORAGE_KEYS.accessToken, accessToken);
    localStorage.setItem(STORAGE_KEYS.refreshToken, refreshToken);
    set({ user });
  },

  logout: () => {
    localStorage.removeItem(STORAGE_KEYS.user);
    localStorage.removeItem(STORAGE_KEYS.accessToken);
    localStorage.removeItem(STORAGE_KEYS.refreshToken);
    set({ user: null });
  },

  setLearningStyle: (learning_style, cluster_id) =>
    set((state) => {
      const user = state.user ? { ...state.user, learning_style, cluster_id } : null;
      if (user) {
        localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user));
      }
      return { user };
    }),
}));

export default useAuthStore;
