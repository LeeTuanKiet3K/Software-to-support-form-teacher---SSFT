// client/lib/apiClient.ts

export const apiClient = async (endpoint: string, options: RequestInit = {}) => {
  // Tự động lấy URL gốc từ file .env.local
  const baseUrl = process.env.NEXT_PUBLIC_API_URL;

  // Gọi API thẳng đến Backend
  const response = await fetch(`${baseUrl}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    let errorMessage = 'Lỗi kết nối đến máy chủ Backend';
    if (errorData.detail) {
      if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        errorMessage = errorData.detail.map((err: any) => err.msg).join(', ');
      } else {
        errorMessage = JSON.stringify(errorData.detail);
      }
    }
    throw new Error(errorMessage);
  }

  return response.json();
};