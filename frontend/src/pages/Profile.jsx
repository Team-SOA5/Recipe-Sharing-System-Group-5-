import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { authAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user, loading: authLoading, fetchUser } = useAuth()
  const [loading, setLoading] = useState(false)
  const [userData, setUserData] = useState(null)
  const [formData, setFormData] = useState({
    fullName: '',
    bio: '',
    location: '',
    website: '',
  })

  // Fetch user data when component mounts
  useEffect(() => {
    loadUserData()
  }, [])

  // Update formData when user or userData changes
  useEffect(() => {
    const currentUser = userData || user
    if (currentUser) {
      setFormData({
        fullName: currentUser.fullName || '',
        bio: currentUser.bio || '',
        location: currentUser.location || '',
        website: currentUser.website || '',
      })
    }
  }, [user, userData])

  const loadUserData = async () => {
    try {
      setLoading(true)
      const data = await authAPI.getCurrentUser()
      console.log('Loaded user data:', data) // Debug log
      setUserData(data)
      // Also update context
      if (fetchUser) {
        await fetchUser()
      }
    } catch (error) {
      console.error('Failed to load user data:', error)
      console.error('Error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      // Nếu không load được, sử dụng user từ context
      if (!user) {
        const errorMessage = error.response?.data?.message || 'Không thể tải thông tin người dùng'
        toast.error(errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const updatedUser = await authAPI.updateProfile(formData)
      setUserData(updatedUser)
      // Refresh user in context
      if (fetchUser) {
        await fetchUser()
      }
      toast.success('Đã cập nhật hồ sơ')
    } catch (error) {
      const message = error.response?.data?.message || 'Không thể cập nhật hồ sơ'
      toast.error(message)
      console.error('Update profile error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAvatarChange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Vui lòng chọn file ảnh')
      return
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File ảnh quá lớn (tối đa 5MB)')
      return
    }

    try {
      setLoading(true)
      const data = await authAPI.updateAvatar(file)
      setUserData(data)
      // Refresh user in context
      if (fetchUser) {
        await fetchUser()
      }
      toast.success('Đã cập nhật ảnh đại diện')
    } catch (error) {
      const message = error.response?.data?.message || 'Không thể cập nhật ảnh đại diện'
      toast.error(message)
      console.error('Update avatar error:', error)
    } finally {
      setLoading(false)
      // Reset file input
      e.target.value = ''
    }
  }

  // Show loading state
  if (authLoading || (loading && !userData && !user)) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    )
  }

  const currentUser = userData || user

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Hồ sơ của tôi</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1">
          <div className="card p-6 text-center">
            <div className="relative inline-block mb-4">
              <img
                src={currentUser?.avatar || 'https://i.pravatar.cc/150?img=1'}
                alt={currentUser?.fullName || 'Avatar'}
                className="w-32 h-32 rounded-full mx-auto object-cover"
              />
              <label className="absolute bottom-0 right-0 bg-primary-600 text-white rounded-full p-2 cursor-pointer hover:bg-primary-700 transition">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarChange}
                  className="hidden"
                  disabled={loading}
                />
              </label>
            </div>
            <h2 className="text-xl font-bold">{currentUser?.fullName || 'Chưa có tên'}</h2>
            <p className="text-gray-500">@{currentUser?.username || 'username'}</p>
            {currentUser?.bio && (
              <p className="text-sm text-gray-600 mt-2">{currentUser.bio}</p>
            )}
          </div>
        </div>

        <div className="md:col-span-2">
          <form onSubmit={handleSubmit} className="card p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Họ và tên
              </label>
              <input
                type="text"
                className="input-field"
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Giới thiệu
              </label>
              <textarea
                className="input-field"
                rows="4"
                value={formData.bio}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Địa chỉ
              </label>
              <input
                type="text"
                className="input-field"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Website
              </label>
              <input
                type="url"
                className="input-field"
                value={formData.website}
                onChange={(e) => setFormData({ ...formData, website: e.target.value })}
              />
            </div>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Đang lưu...' : 'Lưu thay đổi'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}


