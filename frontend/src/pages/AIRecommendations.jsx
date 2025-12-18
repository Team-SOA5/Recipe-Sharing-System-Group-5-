import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { aiAPI } from '../services/api'

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
      setItems(res.data || [])
    } catch (error) {
      console.error('Failed to load AI recommendations', error)
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
                  <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
                    {item.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
