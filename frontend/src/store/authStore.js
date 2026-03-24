import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useAuthStore = create(
  persist(
    (set) => ({
      currentUser: null,

      login: (userData) =>
        set({
          currentUser: userData,
        }),

      logout: () =>
        set({
          currentUser: null,
        }),
    }),
    {
      name: "auth-storage", 
    }
  )
);