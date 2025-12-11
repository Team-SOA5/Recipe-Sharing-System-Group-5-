import { useState } from 'react'
import toast from 'react-hot-toast'

export default function HealthRecords() {
  const [records, setRecords] = useState([])

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Hồ sơ sức khỏe</h1>
        <button className="btn-primary">+ Upload hồ sơ</button>
      </div>

      <div className="card p-6">
        <p className="text-gray-600 mb-4">
          Tính năng này cho phép bạn upload hồ sơ bệnh án (PDF) để nhận gợi ý món ăn phù hợp từ AI.
        </p>
        <p className="text-sm text-gray-500">
          Tính năng đang được phát triển. Sẽ có sẵn khi backend được triển khai.
        </p>
      </div>
    </div>
  )
}

