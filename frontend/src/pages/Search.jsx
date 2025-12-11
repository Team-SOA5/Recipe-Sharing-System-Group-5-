import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { searchAPI, categoryAPI } from '../services/api'
import RecipeCard from '../components/RecipeCard'
import { FiSearch } from 'react-icons/fi'
import toast from 'react-hot-toast'

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [recipes, setRecipes] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    categoryId: searchParams.get('categoryId') || '',
    difficulty: searchParams.get('difficulty') || '',
    sort: searchParams.get('sort') || 'relevance',
  })

  useEffect(() => {
    loadCategories()
    if (query) {
      performSearch()
    }
  }, [])

  const loadCategories = async () => {
    try {
      const data = await categoryAPI.getCategories()
      setCategories(data.data || [])
    } catch (error) {
      console.error(error)
    }
  }

  const performSearch = async () => {
    if (!query.trim()) return

    setLoading(true)
    try {
      const params = { q: query, ...filters }
      const data = await searchAPI.searchRecipes(params)
      setRecipes(data.data || [])
      setSearchParams(params)
    } catch (error) {
      toast.error('Không thể tìm kiếm')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    performSearch()
  }

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Tìm kiếm công thức</h1>

      {/* Search Bar */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Tìm kiếm công thức..."
              className="input-field pl-10"
            />
          </div>
          <button type="submit" className="btn-primary">
            Tìm kiếm
          </button>
        </div>
      </form>

      {/* Filters */}
      {query && (
        <div className="mb-6 flex flex-wrap items-center gap-4">
          <select
            value={filters.categoryId}
            onChange={(e) => handleFilterChange('categoryId', e.target.value)}
            className="input-field"
          >
            <option value="">Tất cả danh mục</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
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
            <option value="relevance">Liên quan nhất</option>
            <option value="newest">Mới nhất</option>
            <option value="most_viewed">Xem nhiều nhất</option>
            <option value="most_liked">Yêu thích nhất</option>
          </select>
        </div>
      )}

      {/* Results */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : query && recipes.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Không tìm thấy kết quả nào</p>
        </div>
      ) : query && recipes.length > 0 ? (
        <>
          <p className="text-gray-600 mb-4">
            Tìm thấy {recipes.length} công thức cho "{query}"
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {recipes.map((recipe) => (
              <RecipeCard key={recipe.id} recipe={recipe} />
            ))}
          </div>
        </>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Nhập từ khóa để tìm kiếm</p>
        </div>
      )}
    </div>
  )
}

