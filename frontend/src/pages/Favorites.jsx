import { useState, useEffect } from 'react'
import { favoriteAPI, recipeAPI, userAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import RecipeCard from '../components/RecipeCard'
import toast from 'react-hot-toast'

export default function Favorites() {
  const [recipes, setRecipes] = useState([])
  const [loading, setLoading] = useState(true)
  const { user, isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated) {
      loadFavorites()
    } else {
      setLoading(false)
    }
  }, [isAuthenticated])

  const loadFavorites = async () => {
    try {
      setLoading(true)
      if (!user) {
        setRecipes([])
        return
      }

      const params = { page: 1, limit: 20, userId: user.id || user.userId || user._id }
      const data = await favoriteAPI.getFavorites(params)
      const favorites = Array.isArray(data) ? data : data?.data || []

      if (favorites.length === 0) {
        setRecipes([])
        return
      }

      // Lấy chi tiết recipe đầy đủ từ recipe-service để dùng cho RecipeCard
      const ids = favorites.map((f) => f.id)
      const results = await Promise.allSettled(ids.map((id) => recipeAPI.getRecipe(id)))

      let detailedRecipes = results
        .filter((r) => r.status === 'fulfilled' && r.value)
        .map((r) => ({
          // r.value đã là response.data do interceptor, là object recipe đầy đủ
          ...r.value,
          isFavorited: true,
        }))

      // Fetch author info cho tất cả recipes
      const authorIds = Array.from(new Set(detailedRecipes.map(r => r.author?.id).filter(Boolean)))
      if (authorIds.length > 0) {
        const authorProfiles = await Promise.allSettled(
          authorIds.map(id => userAPI.getUser(id))
        )
        
        const authorMap = {}
        authorProfiles.forEach((result, index) => {
          if (result.status === 'fulfilled' && result.value) {
            const authorId = authorIds[index]
            authorMap[authorId] = result.value
          }
        })
        
        // Enrich recipes với author info
        detailedRecipes = detailedRecipes.map(recipe => {
          if (recipe.author?.id && authorMap[recipe.author.id]) {
            const authorProfile = authorMap[recipe.author.id]
            return {
              ...recipe,
              author: {
                id: recipe.author.id,
                fullName: authorProfile.fullName || 'Người dùng',
                avatar: authorProfile.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(authorProfile.fullName || 'User')}`,
                username: authorProfile.username || '',
                bio: authorProfile.bio || '',
                recipesCount: authorProfile.recipesCount || 0,
                followersCount: authorProfile.followersCount || 0,
              }
            }
          }
          // Fallback nếu không fetch được
          return {
            ...recipe,
            author: {
              id: recipe.author?.id || '',
              fullName: 'Người dùng',
              avatar: 'https://ui-avatars.com/api/?name=User',
              username: '',
              bio: '',
              recipesCount: 0,
              followersCount: 0,
            }
          }
        })
      }

      setRecipes(detailedRecipes)
    } catch (error) {
      toast.error('Không thể tải danh sách yêu thích')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Công thức yêu thích</h1>

      {!isAuthenticated && (
        <div className="text-center py-12 text-gray-500">
          Vui lòng đăng nhập để xem danh sách yêu thích.
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : recipes.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Bạn chưa có công thức yêu thích nào</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {recipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}
    </div>
  )
}

