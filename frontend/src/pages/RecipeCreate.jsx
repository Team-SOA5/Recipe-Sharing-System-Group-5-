import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { recipeAPI, categoryAPI, tagAPI, mediaAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function RecipeCreate() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [categories, setCategories] = useState([])
  const [tags, setTags] = useState([])
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    categoryId: '',
    difficulty: 'easy',
    cookingTime: '',
    servings: '',
    ingredients: [{ name: '', amount: '', note: '' }],
    instructions: [{ step: 1, description: '', image: '', duration: '' }],
    tags: [],
    thumbnail: '',
  })

  useEffect(() => {
    loadCategories()
    loadTags()
  }, [])

  const loadCategories = async () => {
    try {
      const data = await categoryAPI.getCategories()
      setCategories(data.data || [])
    } catch (error) {
      console.error(error)
    }
  }

  const loadTags = async () => {
    try {
      const data = await tagAPI.getPopularTags(20)
      setTags(data.data || [])
    } catch (error) {
      console.error(error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await recipeAPI.createRecipe(formData)
      toast.success('Đã tạo công thức thành công!')
      navigate('/')
    } catch (error) {
      toast.error('Không thể tạo công thức')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const addIngredient = () => {
    setFormData({
      ...formData,
      ingredients: [...formData.ingredients, { name: '', amount: '', note: '' }],
    })
  }

  const removeIngredient = (index) => {
    setFormData({
      ...formData,
      ingredients: formData.ingredients.filter((_, i) => i !== index),
    })
  }

  const updateIngredient = (index, field, value) => {
    const newIngredients = [...formData.ingredients]
    newIngredients[index][field] = value
    setFormData({ ...formData, ingredients: newIngredients })
  }

  const addInstruction = () => {
    setFormData({
      ...formData,
      instructions: [
        ...formData.instructions,
        {
          step: formData.instructions.length + 1,
          description: '',
          image: '',
          duration: '',
        },
      ],
    })
  }

  const removeInstruction = (index) => {
    const newInstructions = formData.instructions
      .filter((_, i) => i !== index)
      .map((inst, idx) => ({ ...inst, step: idx + 1 }))
    setFormData({ ...formData, instructions: newInstructions })
  }

  const updateInstruction = (index, field, value) => {
    const newInstructions = [...formData.instructions]
    newInstructions[index][field] = value
    setFormData({ ...formData, instructions: newInstructions })
  }

  const toggleTag = (tagId) => {
    const newTags = formData.tags.includes(tagId)
      ? formData.tags.filter((id) => id !== tagId)
      : [...formData.tags, tagId]
    setFormData({ ...formData, tags: newTags })
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">Tạo công thức mới</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4">Thông tin cơ bản</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tên công thức *
              </label>
              <input
                type="text"
                required
                className="input-field"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mô tả
              </label>
              <textarea
                className="input-field"
                rows="3"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Danh mục *
                </label>
                <select
                  required
                  className="input-field"
                  value={formData.categoryId}
                  onChange={(e) => setFormData({ ...formData, categoryId: e.target.value })}
                >
                  <option value="">Chọn danh mục</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Độ khó *
                </label>
                <select
                  required
                  className="input-field"
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                >
                  <option value="easy">Dễ</option>
                  <option value="medium">Trung bình</option>
                  <option value="hard">Khó</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Thời gian nấu (phút) *
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  className="input-field"
                  value={formData.cookingTime}
                  onChange={(e) => setFormData({ ...formData, cookingTime: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Số người ăn *
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  className="input-field"
                  value={formData.servings}
                  onChange={(e) => setFormData({ ...formData, servings: e.target.value })}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Ingredients */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Nguyên liệu *</h2>
            <button
              type="button"
              onClick={addIngredient}
              className="btn-secondary text-sm"
            >
              + Thêm nguyên liệu
            </button>
          </div>
          <div className="space-y-3">
            {formData.ingredients.map((ingredient, index) => (
              <div key={index} className="grid grid-cols-12 gap-2">
                <input
                  type="text"
                  placeholder="Tên nguyên liệu"
                  required
                  className="input-field col-span-4"
                  value={ingredient.name}
                  onChange={(e) => updateIngredient(index, 'name', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Số lượng"
                  required
                  className="input-field col-span-3"
                  value={ingredient.amount}
                  onChange={(e) => updateIngredient(index, 'amount', e.target.value)}
                />
                <input
                  type="text"
                  placeholder="Ghi chú (tùy chọn)"
                  className="input-field col-span-4"
                  value={ingredient.note}
                  onChange={(e) => updateIngredient(index, 'note', e.target.value)}
                />
                {formData.ingredients.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeIngredient(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Instructions */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Cách làm *</h2>
            <button
              type="button"
              onClick={addInstruction}
              className="btn-secondary text-sm"
            >
              + Thêm bước
            </button>
          </div>
          <div className="space-y-4">
            {formData.instructions.map((instruction, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-primary-600">Bước {instruction.step}</span>
                  {formData.instructions.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeInstruction(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      × Xóa
                    </button>
                  )}
                </div>
                <textarea
                  placeholder="Mô tả bước làm..."
                  required
                  className="input-field mb-2"
                  rows="3"
                  value={instruction.description}
                  onChange={(e) => updateInstruction(index, 'description', e.target.value)}
                />
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    placeholder="URL hình ảnh (tùy chọn)"
                    className="input-field"
                    value={instruction.image}
                    onChange={(e) => updateInstruction(index, 'image', e.target.value)}
                  />
                  <input
                    type="number"
                    placeholder="Thời gian (phút)"
                    className="input-field"
                    value={instruction.duration}
                    onChange={(e) => updateInstruction(index, 'duration', e.target.value)}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tags */}
        <div className="card p-6">
          <h2 className="text-xl font-bold mb-4">Tags</h2>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <button
                key={tag.id}
                type="button"
                onClick={() => toggleTag(tag.id)}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  formData.tags.includes(tag.id)
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                #{tag.name}
              </button>
            ))}
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="btn-secondary"
          >
            Hủy
          </button>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Đang tạo...' : 'Tạo công thức'}
          </button>
        </div>
      </form>
    </div>
  )
}

