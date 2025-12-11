import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { userAPI, recipeAPI } from '../services/api'
import RecipeCard from '../components/RecipeCard'
import { FiEdit, FiTrash2, FiPlus, FiAlertCircle } from 'react-icons/fi'
import toast from 'react-hot-toast'

export default function MyRecipes() {
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState(null)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    if (user?.id) {
      loadRecipes()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, isAuthenticated])

  const loadRecipes = async () => {
    if (!user?.id) {
      toast.error('Không tìm thấy thông tin người dùng')
      return
    }
    
    try {
      setLoading(true)
      console.log('Loading recipes for user:', user.id)
      const response = await userAPI.getUserRecipes(user.id)
      console.log('My recipes response:', response)
      // Backend trả về { data: [...], pagination: {...} }
      // Interceptor đã extract response.data, nên response = { data: [...], pagination: {...} }
      setRecipes(response?.data || [])
    } catch (error) {
      console.error('Error loading recipes:', error)
      const errorMessage = error.response?.data?.message || 'Không thể tải danh sách công thức'
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (recipeId) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa công thức này?')) {
      return
    }

    try {
      setDeletingId(recipeId)
      await recipeAPI.deleteRecipe(recipeId)
      toast.success('Đã xóa công thức')
      // Reload recipes
      await loadRecipes()
    } catch (error) {
      console.error('Error deleting recipe:', error)
      const errorMessage = error.response?.data?.message || 'Không thể xóa công thức'
      toast.error(errorMessage)
    } finally {
      setDeletingId(null)
    }
  }

  const handleEdit = (recipeId) => {
    navigate(`/recipes/${recipeId}/edit`)
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Quản lý công thức của tôi</h1>
          <p className="text-gray-600">
            Bạn có {recipes.length} công thức
          </p>
        </div>
        <button
          onClick={() => navigate('/recipes/create')}
          className="btn-primary flex items-center space-x-2"
        >
          <FiPlus />
          <span>Tạo công thức mới</span>
        </button>
      </div>

      {recipes.length === 0 ? (
        <div className="card p-12 text-center">
          <FiAlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Chưa có công thức nào</h2>
          <p className="text-gray-600 mb-6">
            Hãy bắt đầu tạo công thức đầu tiên của bạn!
          </p>
          <button
            onClick={() => navigate('/recipes/create')}
            className="btn-primary"
          >
            Tạo công thức mới
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {recipes.map((recipe) => (
            <div key={recipe.id} className="relative group">
              <RecipeCard recipe={recipe} />
              {/* Action buttons overlay */}
              <div className="absolute top-2 right-2 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleEdit(recipe.id)}
                  className="bg-white p-2 rounded-full shadow-md hover:bg-primary-50 text-primary-600 hover:text-primary-700 transition-colors"
                  title="Chỉnh sửa"
                >
                  <FiEdit />
                </button>
                <button
                  onClick={() => handleDelete(recipe.id)}
                  disabled={deletingId === recipe.id}
                  className="bg-white p-2 rounded-full shadow-md hover:bg-red-50 text-red-600 hover:text-red-700 transition-colors disabled:opacity-50"
                  title="Xóa"
                >
                  {deletingId === recipe.id ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                  ) : (
                    <FiTrash2 />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

