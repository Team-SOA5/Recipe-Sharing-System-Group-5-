import { useEffect, useState, useRef } from 'react'
import toast from 'react-hot-toast'
import { healthAPI } from '../services/api'

export default function HealthRecords() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [title, setTitle] = useState('')
  const [notes, setNotes] = useState('')
  const [file, setFile] = useState(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    loadRecords()
  }, [])

  const loadRecords = async () => {
    try {
      setLoading(true)
      const res = await healthAPI.getMedicalRecords()
      setRecords(res.data || [])
    } catch (error) {
      console.error('Failed to load medical records', error)
      toast.error(error.response?.data?.message || 'Không thể tải hồ sơ sức khỏe')
    } finally {
      setLoading(false)
    }
  }

  const handleChooseFile = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0]
    if (!selected) return

    if (!selected.name.toLowerCase().match(/\.(pdf|png|jpe?g|heic)$/)) {
      toast.error('Chỉ hỗ trợ file PDF, PNG, JPG, JPEG, HEIC')
      return
    }
    setFile(selected)
    if (!title) {
      setTitle(selected.name)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) {
      toast.error('Vui lòng chọn file hồ sơ')
      return
    }
    try {
      setUploading(true)
      const res = await healthAPI.uploadMedicalRecord(file, title, notes)
      const newRecord = res.medicalRecord
      setRecords((prev) => [newRecord, ...prev])
      setFile(null)
      setTitle('')
      setNotes('')
      if (fileInputRef.current) fileInputRef.current.value = ''
      toast.success('Đã upload hồ sơ, AI đang xử lý...')
    } catch (error) {
      console.error('Upload medical record failed', error)
      toast.error(error.response?.data?.message || 'Upload hồ sơ thất bại')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Hồ sơ sức khỏe</h1>
      </div>

      <div className="card p-6 mb-6 space-y-4">
        <h2 className="text-xl font-semibold mb-2">Upload hồ sơ mới</h2>
        <p className="text-gray-600">
          Upload hồ sơ bệnh án (PDF / ảnh) để AI phân tích và gợi ý món ăn phù hợp.
        </p>

        <form onSubmit={handleUpload} className="space-y-4 mt-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              File hồ sơ (PDF / Ảnh)
            </label>
            <div className="flex items-center space-x-3">
              <button
                type="button"
                className="btn-secondary"
                onClick={handleChooseFile}
                disabled={uploading}
              >
                Chọn file
              </button>
              <span className="text-sm text-gray-600">
                {file ? file.name : 'Chưa chọn file'}
              </span>
              <input
                type="file"
                accept=".pdf,image/*"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
              />
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={uploading}>
            {uploading ? 'Đang upload...' : 'Upload hồ sơ'}
          </button>
        </form>
      </div>

      <div className="card p-6">
        <h2 className="text-xl font-semibold mb-4">Lịch sử hồ sơ</h2>
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
          </div>
        ) : records.length === 0 ? (
          <p className="text-gray-500">Chưa có hồ sơ nào. Hãy upload hồ sơ đầu tiên của bạn.</p>
        ) : (
          <div className="space-y-4">
            {records.map((rec) => (
              <div key={rec.id} className="border rounded-lg p-4 flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{rec.title}</h3>
                  <p className="text-sm text-gray-500 mb-1">
                    Trạng thái: <span className="font-medium">{rec.status}</span>
                  </p>
                  {rec.analysisSummary && (
                    <p className="text-sm text-gray-700 mt-1">
                      Tóm tắt: {rec.analysisSummary}
                    </p>
                  )}
                </div>
                <a
                  href={rec.fileUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-600 text-sm hover:underline"
                >
                  Xem file
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
