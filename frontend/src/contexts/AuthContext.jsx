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
    } catch (error) {
      console.error('Failed to fetch user:', error)
      localStorage.removeItem('token')
      setToken(null)
    } finally {
      setLoading(false)
    }
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
      await fetchUser()
      toast.success('Đăng nhập thành công!')
      return { success: true }
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
    isAuthenticated: !!token && !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}


