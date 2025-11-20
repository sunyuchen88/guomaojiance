import { defineStore } from 'pinia';
import { ref } from 'vue';

interface User {
  id: number;
  username: string;
  name: string;
  role: string;
  created_at: string;
  last_login_at?: string;
}

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const isLoggedIn = ref<boolean>(false);

  // Actions
  function setUser(userData: User) {
    user.value = userData;
    isLoggedIn.value = true;
    // Persist user to localStorage
    localStorage.setItem('user', JSON.stringify(userData));
  }

  function setToken(accessToken: string) {
    token.value = accessToken;
    // Persist token to localStorage
    localStorage.setItem('access_token', accessToken);
  }

  function logout() {
    user.value = null;
    token.value = null;
    isLoggedIn.value = false;
    // Clear localStorage
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
  }

  function initializeFromStorage() {
    // Try to restore session from localStorage
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('access_token');

    if (storedUser && storedToken) {
      try {
        user.value = JSON.parse(storedUser);
        token.value = storedToken;
        isLoggedIn.value = true;
      } catch (error) {
        console.error('Failed to parse stored user data:', error);
        logout();
      }
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    setUser,
    setToken,
    logout,
    initializeFromStorage,
  };
});
