// client/lib/api.ts
// Utility wrapper cho fetch API để kết nối với FastAPI backend

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface FetchOptions extends RequestInit {
  headers?: Record<string, string>;
}

export const api = {
  get: async (endpoint: string, options: FetchOptions = {}) => {
    return request(endpoint, { ...options, method: 'GET' });
  },

  post: async (endpoint: string, data: any, options: FetchOptions = {}) => {
    return request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
  },

  put: async (endpoint: string, data: any, options: FetchOptions = {}) => {
    return request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
  },

  patch: async (endpoint: string, data: any, options: FetchOptions = {}) => {
    return request(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
  },

  delete: async (endpoint: string, options: FetchOptions = {}) => {
    return request(endpoint, { ...options, method: 'DELETE' });
  },
};

async function request(endpoint: string, options: FetchOptions) {
  const url = `${BASE_URL}${endpoint}`;
  
  // Có thể chèn Authorization Header ở đây nếu đã đăng nhập
  // const token = localStorage.getItem('token');
  // if (token) {
  //   options.headers = { ...options.headers, 'Authorization': `Bearer ${token}` };
  // }

  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      let errorMessage = 'Lỗi kết nối đến server';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch (e) {
        errorMessage = response.statusText;
      }
      throw new Error(errorMessage);
    }

    // Xử lý response NoContent (204)
    if (response.status === 204) {
      return null;
    }

    return response.json();
  } catch (error) {
    console.error(`[API Error] ${options.method} ${endpoint}:`, error);
    throw error;
  }
}
