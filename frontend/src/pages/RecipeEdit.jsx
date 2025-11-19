import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { recipeAPI } from '../services/api'
import toast from 'react-hot-toast'

export default function RecipeEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  // Tạm thời redirect về create page với thông báo
  useEffect(() => {
    toast('Tính năng chỉnh sửa đang được phát triển')
    navigate(`/recipes/${id}`)
  }, [id, navigate])
  
  return null
}

