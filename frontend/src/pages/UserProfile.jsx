import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { userAPI } from '../services/api'
import RecipeCard from '../components/RecipeCard'
import { FiUser, FiUsers } from 'react-icons/fi'
import toast from 'react-hot-toast'

export default function UserProfile() {
  const { userId } = useParams()
  const [user, setUser] = useState(null)
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('recipes')

  useEffect(() => {
    loadUser()
  }, [userId])

  const loadUser = async () => {
    try {
      setLoading(true)
      const [userData, recipesData] = await Promise.all([
        userAPI.getUser(userId),
        userAPI.getUserRecipes(userId),
      ])
      setUser(userData)
      setRecipes(recipesData.data || [])
    } catch (error) {
      toast.error('Không thể tải thông tin người dùng')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!user) {
    return <div className="text-center py-12">Không tìm thấy người dùng</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* User Info */}
      <div className="card p-8 mb-6">
        <div className="flex items-center space-x-6">
          <img
            src={user.avatar}
            alt={user.fullName}
            className="w-24 h-24 rounded-full"
          />
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2">{user.fullName}</h1>
            <p className="text-gray-500 mb-2">@{user.username}</p>
            {user.bio && <p className="text-gray-600 mb-4">{user.bio}</p>}
            <div className="flex items-center space-x-6 text-sm">
              <span className="flex items-center">
                <FiUser className="mr-1" />
                {user.recipesCount} công thức
              </span>
              <span className="flex items-center">
                <FiUsers className="mr-1" />
                {user.followersCount} người theo dõi
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <div className="flex space-x-4">
          <button
            onClick={() => setActiveTab('recipes')}
            className={`pb-2 px-4 font-medium ${
              activeTab === 'recipes'
                ? 'border-b-2 border-primary-500 text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Công thức ({recipes.length})
          </button>
        </div>
      </div>

      {/* Content */}
      {activeTab === 'recipes' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {recipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}
    </div>
  )
}

