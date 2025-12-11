import axios from 'axios'
import { mockAPI } from './mockData'

// Flag để bật/tắt mock mode
const USE_MOCK = false // Đặt false khi có backend thật

// API Gateway URL (cho các service khác)
const API_BASE_URL = 'http://localhost:8888/api/v1'

// Auth Service URL (gọi trực tiếp)
const AUTH_SERVICE_URL = 'http://localhost:8080'

// Category Service URL (gọi trực tiếp)
const CATEGORY_SERVICE_URL = 'http://localhost:8083'

// User Service URL (gọi trực tiếp)
const USER_SERVICE_URL = 'http://localhost:8081'

// Recipe Service URL (gọi trực tiếp)
const RECIPE_SERVICE_URL = 'http://localhost:8082'

// Axios instance cho API Gateway (các service khác)
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Axios instance riêng cho Auth Service
const authApi = axios.create({
  baseURL: AUTH_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Axios instance riêng cho Category Service
const categoryApi = axios.create({
  baseURL: CATEGORY_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Axios instance riêng cho User Service
const userApi = axios.create({
  baseURL: USER_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Axios instance riêng cho Recipe Service
const recipeApi = axios.create({
  baseURL: RECIPE_SERVICE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor để thêm token vào header cho Category Service
categoryApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor để thêm token vào header cho User Service
userApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor để thêm token vào header cho Recipe Service
recipeApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor để thêm token vào header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor để xử lý lỗi và refresh token cho API Gateway
api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config
    
    // Nếu lỗi 401 và chưa retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = localStorage.getItem('refreshToken')
      const accessToken = localStorage.getItem('token')
      
      // Nếu có refreshToken, thử refresh token
      if (refreshToken && accessToken) {
        try {
          const newTokens = await authAPI.refreshToken(accessToken, refreshToken)
          if (newTokens.accessToken) {
            localStorage.setItem('token', newTokens.accessToken)
            if (newTokens.refreshToken) {
              localStorage.setItem('refreshToken', newTokens.refreshToken)
            }
            // Retry request với token mới
            originalRequest.headers.Authorization = `Bearer ${newTokens.accessToken}`
            return api(originalRequest)
          }
        } catch (refreshError) {
          // Refresh token thất bại, đăng xuất
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // Không có refreshToken, đăng xuất
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

// Helper để chọn giữa mock và real API
const callAPI = async (mockFn, realFn, ...args) => {
  if (USE_MOCK) {
    try {
      return await mockFn(...args)
    } catch (error) {
      throw { response: { data: { message: error.message } } }
    }
  }
  return realFn(...args)
}

// Auth API - Gọi trực tiếp đến Auth Service
export const authAPI = {
  login: async (email, password) => {
    if (USE_MOCK) {
      return await mockAPI.login(email, password)
    }
    try {
      const response = await authApi.post('/auth/login', { email, password })
      // Auth service trả về: { message, accessToken, refreshToken }
      return response.data
    } catch (error) {
      // Xử lý lỗi từ auth service
      if (error.response?.data) {
        throw {
          response: {
            data: {
              code: error.response.data.code,
              message: error.response.data.message || 'Đăng nhập thất bại'
            }
          }
        }
      }
      throw error
    }
  },
  
  register: async (data) => {
    if (USE_MOCK) {
      return await mockAPI.register(data)
    }
    try {
      const response = await authApi.post('/auth/register', {
        email: data.email,
        password: data.password,
        username: data.username,
        fullName: data.fullName
      })
      // Auth service trả về: { message, user: {...} }
      return response.data
    } catch (error) {
      if (error.response?.data) {
        throw {
          response: {
            data: {
              code: error.response.data.code,
              message: error.response.data.message || 'Đăng ký thất bại'
            }
          }
        }
      }
      throw error
    }
  },
  
  logout: async (accessToken, refreshToken) => {
    if (USE_MOCK) {
      return Promise.resolve({})
    }
    try {
      const response = await authApi.post('/auth/logout', {
        accessToken,
        refreshToken
      })
      return response.data
    } catch (error) {
      // Không throw error khi logout để đảm bảo user vẫn có thể đăng xuất
      console.error('Logout error:', error)
      return { message: 'Đã đăng xuất' }
    }
  },
  
  refreshToken: async (accessToken, refreshToken) => {
    if (USE_MOCK) {
      return { accessToken: 'new_token', refreshToken: 'new_refresh_token' }
    }
    try {
      const response = await authApi.post('/auth/refresh-token', {
        accessToken,
        refreshToken
      })
      // Auth service trả về: { accessToken, refreshToken }
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  // User profile API - gọi trực tiếp đến User Service
  getCurrentUser: async () => {
    if (USE_MOCK) {
      return mockAPI.getCurrentUser()
    }
    try {
      // User service trả về: { id, username, fullName, avatar, bio, ... }
      const response = await userApi.get('/users/me')
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  updateProfile: async (data) => {
    if (USE_MOCK) {
      return { message: 'Profile updated' }
    }
    try {
      // User service trả về: { id, username, fullName, avatar, bio, ... }
      const response = await userApi.put('/users/me', data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  updateAvatar: async (file) => {
    if (USE_MOCK) {
      return { avatar: 'https://i.pravatar.cc/150?img=1' }
    }
    try {
      const formData = new FormData()
      formData.append('file', file)
      // User service trả về: { id, username, fullName, avatar, bio, ... }
      const response = await userApi.put('/users/me/avatar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

// Recipe API - gọi trực tiếp đến Recipe Service
export const recipeAPI = {
  getRecipes: async (params = {}) => {
    if (USE_MOCK) {
      return mockAPI.getRecipes(params)
    }
    try {
      // Recipe service trả về: { data: [...], pagination: {...} }
      const response = await recipeApi.get('/recipes', { params })
      // Axios tự động parse response.data, nên response.data đã là object JSON
      return response.data
    } catch (error) {
      console.error('Recipe API error:', error)
      console.error('Error response:', error.response?.data)
      throw error
    }
  },
  
  getRecipe: async (id) => {
    if (USE_MOCK) {
      return mockAPI.getRecipe(id)
    }
    try {
      // Recipe service trả về: { id, title, description, ... }
      const response = await recipeApi.get(`/recipes/${id}`)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  createRecipe: async (data) => {
    if (USE_MOCK) {
      return { id: 'new_recipe_id', ...data }
    }
    try {
      const response = await recipeApi.post('/recipes', data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  updateRecipe: async (id, data) => {
    if (USE_MOCK) {
      return { id, ...data }
    }
    try {
      const response = await recipeApi.put(`/recipes/${id}`, data)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  deleteRecipe: async (id) => {
    if (USE_MOCK) {
      return { message: 'Deleted' }
    }
    try {
      const response = await recipeApi.delete(`/recipes/${id}`)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  incrementView: async (id) => {
    if (USE_MOCK) {
      return { views: 1 }
    }
    try {
      const response = await recipeApi.post(`/recipes/${id}/view`)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  getFeed: async (params = {}) => {
    if (USE_MOCK) {
      return mockAPI.getRecipes(params)
    }
    try {
      // Recipe service trả về: { data: [...] }
      const response = await recipeApi.get('/recipes/feed', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  getTrending: async (params = {}) => {
    if (USE_MOCK) {
      return mockAPI.getRecipes(params)
    }
    try {
      // Recipe service trả về: { data: [...] }
      const response = await recipeApi.get('/recipes/trending/recipes', { params })
      return response.data
    } catch (error) {
      throw error
    }
  },
}

// Category API - Gọi trực tiếp đến Category Service
export const categoryAPI = {
  getCategories: async () => {
    if (USE_MOCK) {
      return await mockAPI.getCategories()
    }
    try {
      const response = await categoryApi.get('/categories')
      // Category service trả về: { data: [...] }
      return response.data
    } catch (error) {
      console.error('Category API error:', error)
      throw error
    }
  },

  getCategory: async (id) => {
    if (USE_MOCK) {
      return await mockAPI.getCategory(id)
    }
    try {
      const response = await categoryApi.get(`/categories/${id}`)
      return response.data
    } catch (error) {
      console.error('Category API error:', error)
      throw error
    }
  },

  createCategory: async (data) => {
    try {
      const response = await categoryApi.post('/categories', data)
      return response.data
    } catch (error) {
      console.error('Category API error:', error)
      throw error
    }
  },

  updateCategory: async (id, data) => {
    try {
      const response = await categoryApi.put(`/categories/${id}`, data)
      return response.data
    } catch (error) {
      console.error('Category API error:', error)
      throw error
    }
  },

  deleteCategory: async (id) => {
    try {
      const response = await categoryApi.delete(`/categories/${id}`)
      return response.data
    } catch (error) {
      console.error('Category API error:', error)
      throw error
    }
  },
}

// Tag API
export const tagAPI = {
  getTags: (params) => api.get('/tags', { params }),
  
  getPopularTags: (limit) => 
    callAPI(() => mockAPI.getPopularTags(limit), () => api.get('/tags/popular', { params: { limit } })),
  
  createTag: (name) => api.post('/tags', { name }),
}

// Comment API
export const commentAPI = {
  getComments: (recipeId, params) =>
    callAPI(() => mockAPI.getComments(recipeId, params), () => api.get(`/recipes/${recipeId}/comments`, { params })),
  
  createComment: (recipeId, data) =>
    api.post(`/recipes/${recipeId}/comments`, data),
  
  updateComment: (commentId, data) =>
    api.put(`/comments/${commentId}`, data),
  
  deleteComment: (commentId) => api.delete(`/comments/${commentId}`),
  
  likeComment: (commentId) => api.post(`/comments/${commentId}/like`),
  
  unlikeComment: (commentId) => api.delete(`/comments/${commentId}/like`),
}

// Rating API
export const ratingAPI = {
  getRatings: (recipeId) =>
    callAPI(() => mockAPI.getRatings(recipeId), () => api.get(`/recipes/${recipeId}/ratings`)),
  
  createRating: (recipeId, data) =>
    api.post(`/recipes/${recipeId}/ratings`, data),
  
  getMyRating: (recipeId) => api.get(`/recipes/${recipeId}/ratings/me`),
  
  updateRating: (recipeId, data) =>
    api.put(`/recipes/${recipeId}/ratings/me`, data),
  
  deleteRating: (recipeId) => api.delete(`/recipes/${recipeId}/ratings/me`),
}

// Favorite API
export const favoriteAPI = {
  getFavorites: (params) => api.get('/favorites', { params }),
  
  addFavorite: (recipeId) => api.post(`/recipes/${recipeId}/favorite`),
  
  removeFavorite: (recipeId) => api.delete(`/recipes/${recipeId}/favorite`),
}

// Follow API
export const followAPI = {
  follow: (userId) => api.post(`/users/${userId}/follow`),
  
  unfollow: (userId) => api.delete(`/users/${userId}/follow`),
}

// Search API
export const searchAPI = {
  searchRecipes: (params) =>
    callAPI(() => mockAPI.searchRecipes(params), () => api.get('/search/recipes', { params })),
  
  searchUsers: (params) => api.get('/search/users', { params }),
  
  getSuggestions: (q, limit) =>
    api.get('/search/suggestions', { params: { q, limit } }),
}

// Media API
export const mediaAPI = {
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', 'image')
    return api.post('/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// User API
export const userAPI = {
  getUser: async (userId) => {
    if (USE_MOCK) {
      return mockAPI.getUser(userId)
    }
    try {
      // User service trả về: { id, username, fullName, avatar, bio, ... }
      const response = await userApi.get(`/users/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  getUserRecipes: (userId, params) =>
    callAPI(() => mockAPI.getUserRecipes(userId, params), () => api.get(`/users/${userId}/recipes`, { params })),
  
  getUserFavorites: (userId, params) =>
    api.get(`/users/${userId}/favorites`, { params }),
  
  getFollowers: (userId, params) =>
    api.get(`/users/${userId}/followers`, { params }),
  
  getFollowing: (userId, params) =>
    api.get(`/users/${userId}/following`, { params }),
}

// Health API
export const healthAPI = {
  getMedicalRecords: (params) =>
    api.get('/health/medical-records', { params }),
  
  uploadMedicalRecord: (file, title, notes) => {
    const formData = new FormData()
    formData.append('file', file)
    if (title) formData.append('title', title)
    if (notes) formData.append('notes', notes)
    return api.post('/health/medical-records', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  
  getMedicalRecord: (recordId) =>
    api.get(`/health/medical-records/${recordId}`),
  
  deleteMedicalRecord: (recordId) =>
    api.delete(`/health/medical-records/${recordId}`),
  
  reprocessMedicalRecord: (recordId) =>
    api.post(`/health/medical-records/${recordId}/reprocess`),
}

// AI API
export const aiAPI = {
  analyze: (data) => api.post('/ai/analyze', data),
  
  getRecommendations: (params) => api.get('/ai/recommendations', { params }),
  
  getRecommendation: (recommendationId) =>
    api.get(`/ai/recommendations/${recommendationId}`),
  
  deleteRecommendation: (recommendationId) =>
    api.delete(`/ai/recommendations/${recommendationId}`),
  
  sendFeedback: (recommendationId, data) =>
    api.post(`/ai/recommendations/${recommendationId}/feedback`, data),
  
  chat: (data) => api.post('/ai/chat', data),
}

export default api
