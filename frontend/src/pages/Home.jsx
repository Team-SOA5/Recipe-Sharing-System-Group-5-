import { useState, useEffect } from 'react'
import { recipeAPI, categoryAPI, userAPI } from '../services/api'
import RecipeCard from '../components/RecipeCard'
import { FiFilter, FiTrendingUp } from 'react-icons/fi'
import toast from 'react-hot-toast'

export default function Home() {
  const [allRecipes, setAllRecipes] = useState([]) // Lưu tất cả recipes
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({
    categoryId: '',
    difficulty: '',
    sort: 'newest',
  })

  const ITEMS_PER_PAGE = 4

  useEffect(() => {
    setPage(1) // Reset về trang 1 khi filter thay đổi
  }, [filters])

  useEffect(() => {
    loadData()
  }, [filters]) // Chỉ load lại khi filter thay đổi, không load khi page thay đổi

  const loadData = async () => {
    try {
      setLoading(true)
      const params = {
        ...filters,
        // Không gửi page và limit, load tất cả
      }
      const [recipesData, categoriesData] = await Promise.all([
        recipeAPI.getRecipes(params),
        categoryAPI.getCategories(),
      ])
      // Recipes trả về { data: [...], pagination: {...} }
      console.log('Recipes data:', recipesData)
      let recipesList = recipesData?.data || recipesData || []
      
      // Fetch author info cho tất cả recipes
      const authorIds = Array.from(new Set(recipesList.map(r => r.author?.id).filter(Boolean)))
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
        recipesList = recipesList.map(recipe => {
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
      
      setAllRecipes(recipesList) // Lưu tất cả recipes
      
      // Categories trả về { data: [...] } từ category service
      console.log('Categories data:', categoriesData)
      setCategories(categoriesData?.data || categoriesData || [])
    } catch (error) {
      toast.error('Không thể tải dữ liệu')
      console.error('Load data error:', error)
      console.error('Error details:', error.response?.data || error.message)
      // Set empty arrays để tránh lỗi render
      setAllRecipes([])
      setCategories([])
    } finally {
      setLoading(false)
    }
  }

  // Tính toán pagination và recipes hiển thị ở client-side
  const totalPages = Math.ceil(allRecipes.length / ITEMS_PER_PAGE)
  const startIndex = (page - 1) * ITEMS_PER_PAGE
  const endIndex = startIndex + ITEMS_PER_PAGE
  const displayedRecipes = allRecipes.slice(startIndex, endIndex)

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl p-8 mb-8 text-white">
        <h1 className="text-4xl font-bold mb-4">Chia sẻ công thức nấu ăn</h1>
        <p className="text-xl mb-6">
          Khám phá hàng ngàn công thức nấu ăn từ cộng đồng
        </p>
      </div>

      {/* Categories */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Danh mục</h2>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={() => handleFilterChange('categoryId', '')}
            className={`px-4 py-2 rounded-full transition-colors ${
              filters.categoryId === ''
                ? 'bg-primary-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Tất cả
          </button>
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => handleFilterChange('categoryId', category.id)}
              className={`px-4 py-2 rounded-full transition-colors flex items-center space-x-2 ${
                filters.categoryId === category.id
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <span>{category.icon}</span>
              <span>{category.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <div className="flex items-center space-x-2">
          <FiFilter />
          <span className="font-medium">Lọc:</span>
        </div>
        <select
          value={filters.difficulty}
          onChange={(e) => handleFilterChange('difficulty', e.target.value)}
          className="input-field"
        >
          <option value="">Tất cả độ khó</option>
          <option value="easy">Dễ</option>
          <option value="medium">Trung bình</option>
          <option value="hard">Khó</option>
        </select>
        <select
          value={filters.sort}
          onChange={(e) => handleFilterChange('sort', e.target.value)}
          className="input-field"
        >
          <option value="newest">Mới nhất</option>
          <option value="most_viewed">Xem nhiều nhất</option>
          <option value="most_liked">Yêu thích nhất</option>
          <option value="trending">Đang hot</option>
        </select>
      </div>

      {/* Recipes Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : allRecipes.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Không tìm thấy công thức nào</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {displayedRecipes.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Trước
              </button>
              
              <div className="flex space-x-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => {
                  // Chỉ hiển thị một số trang xung quanh trang hiện tại
                  if (
                    pageNum === 1 ||
                    pageNum === totalPages ||
                    (pageNum >= page - 1 && pageNum <= page + 1)
                  ) {
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`px-4 py-2 border rounded-lg transition-colors ${
                          page === pageNum
                            ? 'bg-primary-500 text-white border-primary-500'
                            : 'border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  } else if (pageNum === page - 2 || pageNum === page + 2) {
                    return (
                      <span key={pageNum} className="px-2 py-2">
                        ...
                      </span>
                    )
                  }
                  return null
                })}
              </div>

              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Sau
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

