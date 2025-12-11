import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'
import { useAuth } from '../contexts/AuthContext'

export default function GoogleCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('processing')
  const { syncTokenFromStorage } = useAuth()
  const hasHandledRef = useRef(false)

  useEffect(() => {
    const handleCallback = async () => {
      // React StrictMode runs effects twice in dev; guard to avoid double-processing
      if (hasHandledRef.current) return
      hasHandledRef.current = true

      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')

      const storedState = sessionStorage.getItem('google_oauth_state') || localStorage.getItem('google_oauth_state')
      const codeVerifier = sessionStorage.getItem('google_code_verifier') || localStorage.getItem('google_code_verifier')

      console.log('Google OAuth callback - code:', code)
      console.log('Google OAuth callback - error:', error)
      console.log('Google OAuth callback - state:', state)

      if (error) {
        setStatus('error')
        toast.error('Đăng nhập Google bị hủy')
        setTimeout(() => navigate('/login'), 2000)
        return
      }

      if (!code) {
        setStatus('error')
        toast.error('Thiếu mã xác thực từ Google')
        setTimeout(() => navigate('/login'), 2000)
        return
      }

      if (!codeVerifier) {
        setStatus('error')
        toast.error('Thiếu mã xác thực (code_verifier). Vui lòng thử lại.')
        // Clean any stale data to allow a fresh login
        sessionStorage.removeItem('google_oauth_state')
        sessionStorage.removeItem('google_code_verifier')
        localStorage.removeItem('google_oauth_state')
        localStorage.removeItem('google_code_verifier')
        setTimeout(() => navigate('/login'), 2000)
        return
      }

      if (!state || !storedState || state !== storedState) {
        setStatus('error')
        toast.error('Yêu cầu đăng nhập không hợp lệ. Vui lòng thử lại.')
        setTimeout(() => navigate('/login'), 2000)
        return
      }

      try {
        setStatus('processing')
        const result = await authAPI.googleCallback(code, codeVerifier, state)
        
        // Save tokens to localStorage
        localStorage.setItem('token', result.accessToken)
        localStorage.setItem('refreshToken', result.refreshToken)

        // Update AuthContext state so header re-renders
        await syncTokenFromStorage()

        // Clean up temporary OAuth data
        sessionStorage.removeItem('google_oauth_state')
        sessionStorage.removeItem('google_code_verifier')
        localStorage.removeItem('google_oauth_state')
        localStorage.removeItem('google_code_verifier')
        
        setStatus('success')
        toast.success('Đăng nhập Google thành công!')
        
        // Redirect to home page
        setTimeout(() => navigate('/'), 1000)
      } catch (error) {
        console.error('Google callback error:', error)
        setStatus('error')
        const errorMessage = error?.response?.data?.message || 'Đăng nhập Google thất bại'
        toast.error(errorMessage)
        setTimeout(() => navigate('/login'), 2000)
      }
    }

    handleCallback()
  }, [searchParams, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 text-center">
        {status === 'processing' && (
          <>
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600"></div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              Đang xử lý đăng nhập Google...
            </h2>
            <p className="text-gray-600">Vui lòng đợi trong giây lát</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="flex justify-center">
              <svg className="h-16 w-16 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              Đăng nhập thành công!
            </h2>
            <p className="text-gray-600">Đang chuyển hướng...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="flex justify-center">
              <svg className="h-16 w-16 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              Đăng nhập thất bại
            </h2>
            <p className="text-gray-600">Đang chuyển về trang đăng nhập...</p>
          </>
        )}
      </div>
    </div>
  )
}
