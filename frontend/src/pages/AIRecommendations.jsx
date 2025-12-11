import { useState } from 'react'
import toast from 'react-hot-toast'

export default function AIRecommendations() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">Gợi ý món ăn từ AI</h1>

      <div className="card p-6">
        <p className="text-gray-600 mb-4">
          Dựa trên hồ sơ sức khỏe của bạn, AI sẽ phân tích và gợi ý các món ăn phù hợp với tình trạng sức khỏe.
        </p>
        <p className="text-sm text-gray-500">
          Tính năng đang được phát triển. Sẽ có sẵn khi backend được triển khai.
        </p>
      </div>
    </div>
  )
}

