import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { FiSearch, FiHeart, FiUser, FiLogOut, FiPlus } from 'react-icons/fi'

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-primary-600">🍳</span>
            <span className="text-xl font-bold text-gray-900">Cookpad</span>
          </Link>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl mx-8">
            <Link
              to="/search"
              className="flex items-center w-full bg-gray-100 rounded-full px-4 py-2 text-gray-600 hover:bg-gray-200 transition-colors"
            >
              <FiSearch className="mr-2" />
              <span>Tìm kiếm công thức...</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link
                  to="/recipes/create"
                  className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 font-medium"
                >
                  <FiPlus />
                  <span className="hidden md:inline">Viết món mới</span>
                </Link>
                <Link
                  to="/favorites"
                  className="flex items-center space-x-1 text-gray-700 hover:text-primary-600"
                >
                  <FiHeart />
                  <span className="hidden md:inline">Yêu thích</span>
                </Link>
                <div className="relative group">
                  <button className="flex items-center space-x-2 text-gray-700 hover:text-primary-600">
                    <img
                      src={user?.avatar || 'https://i.pravatar.cc/150?img=1'}
                      alt={user?.fullName}
                      className="w-8 h-8 rounded-full"
                    />
                    <span className="hidden md:inline">{user?.fullName}</span>
                  </button>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <Link
                      to="/profile"
                      className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-t-lg"
                    >
                      <FiUser className="inline mr-2" />
                      Hồ sơ
                    </Link>
                    <Link
                      to="/health"
                      className="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                    >
                      Sức khỏe
                    </Link>
                    <Link
                      to="/ai-recommendations"
                      className="block px-4 py-2 text-gray-700 hover:bg-gray-100"
                    >
                      Gợi ý AI
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-b-lg"
                    >
                      <FiLogOut className="inline mr-2" />
                      Đăng xuất
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-primary-600 font-medium"
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="btn-primary"
                >
                  Đăng ký
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}

