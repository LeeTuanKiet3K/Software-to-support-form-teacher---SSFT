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
    throw new Error(errorData.detail || 'Lỗi kết nối đến máy chủ Backend');
  }

  return response.json();
};