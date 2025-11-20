import api from '@/services/api';
import { message } from 'ant-design-vue';
import router from '@/router';

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add JWT token to headers if available
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      // Handle 401 Unauthorized - token expired or invalid
      if (status === 401) {
        message.error('登录已过期，请重新登录');
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        router.push('/login');
      }
      // Handle 403 Forbidden
      else if (status === 403) {
        message.error(data.detail || '无权限访问');
      }
      // Handle 404 Not Found
      else if (status === 404) {
        message.error(data.detail || '请求的资源不存在');
      }
      // Handle 500 Internal Server Error
      else if (status === 500) {
        message.error('服务器错误，请稍后重试');
      }
      // Handle other errors
      else {
        message.error(data.detail || '请求失败');
      }
    } else if (error.request) {
      // Request was made but no response received
      message.error('网络错误，请检查网络连接');
    } else {
      // Something else happened
      message.error('请求失败: ' + error.message);
    }

    return Promise.reject(error);
  }
);

export default api;
