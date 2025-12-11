import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const data = await authAPI.getCurrentUser()
      setUser(data)
      return { success: true, user: data }
    } catch (error) {
      console.error('Failed to fetch user:', error)
      // Nếu là lỗi 404 (user chưa có profile), không xóa token
      // Chỉ xóa token nếu là lỗi 401 (unauthorized)
      if (error.response?.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        setToken(null)
        setUser(null)
      }
      // Nếu là lỗi khác (404, 500, etc), vẫn giữ token nhưng không set user
      return { success: false, error }
    } finally {
      setLoading(false)
    }
  }

  const syncTokenFromStorage = async () => {
    const storedToken = localStorage.getItem('token')
    if (storedToken && storedToken !== token) {
      setToken(storedToken)
      return fetchUser()
    }
    if (!storedToken) {
      setUser(null)
      setToken(null)
    }
    return { success: !!storedToken }
  }

  const login = async (email, password) => {
    try {
      const response = await authAPI.login(email, password)
      // Auth service trả về: { message, accessToken, refreshToken }
      const { accessToken, refreshToken } = response
      
      if (!accessToken) {
        toast.error('Đăng nhập thất bại: Không nhận được token')
        return { success: false, error: 'Không nhận được token' }
      }
      
      localStorage.setItem('token', accessToken)
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken)
      }
      setToken(accessToken)
      
      // Đợi fetchUser hoàn thành với timeout, nhưng không block nếu fail
      try {
        // Tạo promise với timeout 5 giây
        const fetchUserPromise = fetchUser()
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 5000)
        )
        
        const fetchResult = await Promise.race([fetchUserPromise, timeoutPromise])
        
        // Nếu fetchUser thành công hoặc chỉ là lỗi 404 (user chưa có profile), vẫn cho phép đăng nhập
        if (fetchResult.success || (fetchResult.error?.response?.status === 404)) {
          toast.success('Đăng nhập thành công!')
          return { success: true }
        }
        // Nếu là lỗi 401, đăng nhập thất bại
        if (fetchResult.error?.response?.status === 401) {
          toast.error('Phiên đăng nhập không hợp lệ')
          return { success: false, error: 'Phiên đăng nhập không hợp lệ' }
        }
        // Các lỗi khác, vẫn cho phép đăng nhập (có thể user chưa có profile)
        toast.success('Đăng nhập thành công!')
        return { success: true }
      } catch (fetchError) {
        // Nếu fetchUser timeout hoặc throw error, vẫn cho phép đăng nhập
        console.warn('Could not fetch user profile, but login succeeded:', fetchError)
        toast.success('Đăng nhập thành công!')
        return { success: true }
      }
    } catch (error) {
      const message = error.response?.data?.message || 'Đăng nhập thất bại'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const register = async (userData) => {
    try {
      await authAPI.register(userData)
      toast.success('Đăng ký thành công! Vui lòng đăng nhập.')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.message || 'Đăng ký thất bại'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const logout = async () => {
    try {
      const accessToken = localStorage.getItem('token')
      const refreshToken = localStorage.getItem('refreshToken')
      if (accessToken && refreshToken) {
        await authAPI.logout(accessToken, refreshToken)
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      setToken(null)
      setUser(null)
      toast.success('Đã đăng xuất')
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    syncTokenFromStorage,
    isAuthenticated: !!token, // Chỉ cần token, không cần user (user có thể chưa có profile)
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}


