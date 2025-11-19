import { useState, useEffect } from 'react'
import { recipeAPI, categoryAPI } from '../services/api'
import RecipeCard from '../components/RecipeCard'
import { FiFilter, FiTrendingUp } from 'react-icons/fi'
import toast from 'react-hot-toast'

export default function Home() {
  const [recipes, setRecipes] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    categoryId: '',
    difficulty: '',
    sort: 'newest',
  })

  useEffect(() => {
    loadData()
  }, [filters])

  const loadData = async () => {
    try {
      setLoading(true)
      const [recipesData, categoriesData] = await Promise.all([
        recipeAPI.getRecipes(filters),
        categoryAPI.getCategories(),
      ])
      setRecipes(recipesData.data || [])
      setCategories(categoriesData.data || [])
    } catch (error) {
      toast.error('Không thể tải dữ liệu')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

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
        <div className="flex items-center space-x-2">
          <FiTrendingUp />
          <span>Hơn 10,000 công thức đang chờ bạn khám phá</span>
        </div>
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
      ) : recipes.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Không tìm thấy công thức nào</p>
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

