import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'
import { aiAPI, recipeAPI } from '../services/api'

export default function AIRecommendations() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadRecommendations()
  }, [])

  const loadRecommendations = async () => {
    try {
      setLoading(true)
      const res = await aiAPI.getRecommendations()
      console.log('AI Recommendations API Response:', res)
      
      // Axios interceptor đã extract response.data, nên res là { data: [...], pagination: {...} }
      const recommendations = res?.data || []
      console.log('Parsed recommendations:', recommendations)
      console.log('Number of recommendations:', recommendations.length)
      
      // Fetch recipe details cho mỗi recommendation
      const enrichedItems = await Promise.all(
        recommendations.map(async (item) => {
          if (Array.isArray(item.recommendations) && item.recommendations.length > 0) {
            const enrichedRecs = await Promise.allSettled(
              item.recommendations.map(async (rec) => {
                const recipeId = typeof rec === 'object' ? rec.recipeId : rec
                try {
                  const recipeData = await recipeAPI.getRecipe(recipeId)
                  return {
                    ...rec,
                    recipeId,
                    recipeName: recipeData?.title || `Recipe ${recipeId}`,
                    recipe: recipeData
                  }
                } catch (error) {
                  console.error(`Failed to fetch recipe ${recipeId}:`, error)
                  return {
                    ...rec,
                    recipeId,
                    recipeName: `Recipe ${recipeId}`,
                    recipe: null
                  }
                }
              })
            )
            
            return {
              ...item,
              recommendations: enrichedRecs
                .filter(r => r.status === 'fulfilled')
                .map(r => r.value)
            }
          }
          return item
        })
      )
      
      setItems(enrichedItems)
    } catch (error) {
      console.error('Failed to load AI recommendations', error)
      console.error('Error details:', error.response?.data)
      toast.error(error.response?.data?.message || 'Không thể tải gợi ý từ AI')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Gợi ý món ăn từ AI</h1>

      <div className="card p-6 mb-6">
        <p className="text-gray-600 mb-2">
          Dựa trên hồ sơ sức khỏe đã upload, AI sẽ phân tích và gợi ý các món ăn phù hợp.
        </p>
        <p className="text-sm text-gray-500">
          Mỗi lần bạn upload hồ sơ mới ở mục <strong>Hồ sơ sức khỏe</strong>, hệ thống sẽ tự động chạy
          pipeline AI và lưu kết quả tại đây.
        </p>
      </div>

      <div className="card p-6">
        <h2 className="text-xl font-semibold mb-4">Lịch sử gợi ý</h2>
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
          </div>
        ) : items.length === 0 ? (
          <p className="text-gray-500">
            Chưa có gợi ý nào. Hãy upload hồ sơ sức khỏe trước, sau đó quay lại đây.
          </p>
        ) : (
          <div className="space-y-4">
            {items.map((item) => (
              <div key={item.id} className="border rounded-lg p-4 space-y-2">
                <p className="text-xs text-gray-500">
                  Hồ sơ: <span className="font-medium">{item.medicalRecordId}</span> •{' '}
                  {item.createdAt}
                </p>
                {item.analysisSummary && (
                  <p className="text-sm text-gray-700 mb-2">
                    <span className="font-medium">Tóm tắt phân tích:</span> {item.analysisSummary}
                  </p>
                )}
                {Array.isArray(item.recommendations) && item.recommendations.length > 0 && (
                  <div className="space-y-3">
                    <p className="font-medium text-sm text-gray-700">Món ăn được gợi ý:</p>
                    <ul className="space-y-2">
                      {item.recommendations.map((rec, idx) => {
                        // rec có thể là object {recipeId, reason, recipeName, recipe} hoặc string
                        const recipeId = typeof rec === 'object' ? rec.recipeId : rec
                        const reason = typeof rec === 'object' ? rec.reason : ''
                        const recipeName = typeof rec === 'object' ? rec.recipeName : null
                        const recipe = typeof rec === 'object' ? rec.recipe : null
                        
                        return (
                          <li key={idx} className="border-l-4 border-primary-500 pl-3 py-2 bg-gray-50 rounded-r">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1">
                                {recipeName ? (
                                  <Link 
                                    to={`/recipes/${recipeId}`}
                                    className="font-medium text-sm text-primary-600 hover:text-primary-700 hover:underline"
                                  >
                                    {recipeName}
                                  </Link>
                                ) : (
                                  <p className="font-medium text-sm text-gray-800">
                                    Món ăn ID: {recipeId}
                                  </p>
                                )}
                                {reason && (
                                  <p className="text-xs text-gray-600 mt-1">{reason}</p>
                                )}
                              </div>
                            </div>
                          </li>
                        )
                      })}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
