import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { recipeAPI, commentAPI, ratingAPI, userAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { FiClock, FiUsers, FiStar, FiEye, FiHeart, FiMessageCircle, FiShare2 } from 'react-icons/fi'
import { formatDistanceToNow } from 'date-fns'
import toast from 'react-hot-toast'

export default function RecipeDetail() {
  const { id } = useParams()
  const { isAuthenticated, user } = useAuth()
  const [recipe, setRecipe] = useState(null)
  const [comments, setComments] = useState([])
  const [ratings, setRatings] = useState(null)
  const [myRating, setMyRating] = useState(null)
  const [loading, setLoading] = useState(true)
  const [newComment, setNewComment] = useState('')
  const [ratingValue, setRatingValue] = useState(0)
  const [editingCommentId, setEditingCommentId] = useState(null)
  const [editingContent, setEditingContent] = useState('')
  const [commentToDelete, setCommentToDelete] = useState(null)

  useEffect(() => {
    loadRecipe()
  }, [id])

  const loadRecipe = async () => {
    try {
      setLoading(true)
      console.log('Loading recipe:', id)
      
      // Load recipe first (required)
      const recipeData = await recipeAPI.getRecipe(id)
      console.log('Recipe data:', recipeData)
      setRecipe(recipeData)

      // Sidebar thống kê đánh giá: dùng số liệu tổng hợp từ recipe-service
      setRatings({
        averageRating: recipeData.averageRating || 0,
        totalRatings: recipeData.ratingsCount || 0,
      })
      
      // Load comments riêng với error handling
      try {
        const commentsData = await commentAPI.getComments(id)
        console.log('Comments data:', commentsData)

        const normalizeComments = async (raw) => {
          if (!Array.isArray(raw)) return []

          // Thu thập danh sách authorId dạng string
          const authorIds = Array.from(
            new Set(
              raw
                .map((c) => (typeof c.author === 'string' ? c.author : null))
                .filter((id) => id && id !== 'anonymous')
            )
          )

          // Gọi user-service để lấy profile cho từng authorId (trừ current user đã có sẵn)
          const profileMap = {}
          await Promise.allSettled(
            authorIds.map(async (authorId) => {
              try {
                // Nếu là current user thì dùng context
                if (
                  user &&
                  (authorId === user.id ||
                    authorId === user.userId ||
                    authorId === user._id)
                ) {
                  profileMap[authorId] = user
                  return
                }
                const profile = await userAPI.getUser(authorId)
                profileMap[authorId] = profile
              } catch (e) {
                // Nếu lỗi thì để trống, sẽ fallback avatar/name mặc định
                console.warn('Failed to load author profile for', authorId, e)
              }
            })
          )

          return raw.map((c) => {
            let authorObj = c.author

            if (typeof c.author === 'string') {
              const authorId = c.author
              const profile = profileMap[authorId]

              if (profile) {
                authorObj = {
                  id: profile.id || profile.userId || authorId,
                  fullName: profile.fullName || 'Người dùng',
                  avatar:
                    profile.avatar ||
                    'https://ui-avatars.com/api/?name=' +
                      encodeURIComponent(profile.fullName || 'User'),
                }
              } else if (
                user &&
                (authorId === user.id ||
                  authorId === user.userId ||
                  authorId === user._id)
              ) {
                authorObj = {
                  id: user.id || user.userId || authorId,
                  fullName: user.fullName || 'Bạn',
                  avatar:
                    user.avatar ||
                    'https://ui-avatars.com/api/?name=' +
                      encodeURIComponent(user.fullName || 'User'),
                }
              } else {
                authorObj = {
                  id: authorId,
                  fullName: 'Người dùng',
                  avatar: 'https://ui-avatars.com/api/?name=User',
                }
              }
            }

            return {
              id: c.id,
              content: c.content,
              images: c.images || [],
              createdAt: c.createdAt || c.created_at,
              author: authorObj,
            }
          })
        }

        const normalized = await normalizeComments(commentsData)
        setComments(normalized)
      } catch (commentError) {
        console.warn('Failed to load comments:', commentError)
        setComments([]) // Set empty array on error
        // Don't show error toast for comments, as they might not be implemented yet
      }

      // Không dùng list rating từ comment-service cho thống kê tổng,
      // vì recipe-service đã có sẵn averageRating + ratingsCount chuẩn.
      
      if (isAuthenticated) {
        try {
          const myRatingData = await ratingAPI.getMyRating(id)
          console.log('My rating:', myRatingData)
          setMyRating(myRatingData)
          if (myRatingData && myRatingData.rating) {
            setRatingValue(myRatingData.rating)
          }
        } catch (error) {
          console.log('No rating yet or error:', error)
          // Chưa có rating hoặc lỗi (có thể 404) - this is OK
        }
      }
      
      // Increment view
      recipeAPI.incrementView(id).catch(console.error)
    } catch (error) {
      console.error('Error loading recipe:', error)
      console.error('Error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      toast.error('Không thể tải công thức')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitComment = async (e) => {
    e.preventDefault()
    if (!isAuthenticated) {
      toast.error('Vui lòng đăng nhập để bình luận')
      return
    }
    if (!newComment.trim()) return

    try {
      const payload = {
        content: newComment,
        authorId: user?.id || user?.userId || user?._id,
      }
      const comment = await commentAPI.createComment(id, payload)
      console.log('Created comment:', comment)
      // Reload comments instead of manually adding để thống nhất với backend comment-service
      const commentsData = await commentAPI.getComments(id)

      const normalizeComments = async (raw) => {
        if (!Array.isArray(raw)) return []

        const authorIds = Array.from(
          new Set(
            raw
              .map((c) => (typeof c.author === 'string' ? c.author : null))
              .filter((id) => id && id !== 'anonymous')
          )
        )

        const profileMap = {}
        await Promise.allSettled(
          authorIds.map(async (authorId) => {
            try {
              if (
                user &&
                (authorId === user.id ||
                  authorId === user.userId ||
                  authorId === user._id)
              ) {
                profileMap[authorId] = user
                return
              }
              const profile = await userAPI.getUser(authorId)
              profileMap[authorId] = profile
            } catch (e) {
              console.warn('Failed to load author profile for', authorId, e)
            }
          })
        )

        return raw.map((c) => {
          let authorObj = c.author

          if (typeof c.author === 'string') {
            const authorId = c.author
            const profile = profileMap[authorId]

            if (profile) {
              authorObj = {
                id: profile.id || profile.userId || authorId,
                fullName: profile.fullName || 'Người dùng',
                avatar:
                  profile.avatar ||
                  'https://ui-avatars.com/api/?name=' +
                    encodeURIComponent(profile.fullName || 'User'),
              }
            } else if (
              user &&
              (authorId === user.id ||
                authorId === user.userId ||
                authorId === user._id)
            ) {
              authorObj = {
                id: user.id || user.userId || authorId,
                fullName: user.fullName || 'Bạn',
                avatar:
                  user.avatar ||
                  'https://ui-avatars.com/api/?name=' +
                    encodeURIComponent(user.fullName || 'User'),
              }
            } else {
              authorObj = {
                id: authorId,
                fullName: 'Người dùng',
                avatar: 'https://ui-avatars.com/api/?name=User',
              }
            }
          }

          return {
            id: c.id,
            content: c.content,
            images: c.images || [],
            createdAt: c.createdAt || c.created_at,
            author: authorObj,
          }
        })
      }

      const normalized = await normalizeComments(commentsData)
      setComments(normalized)
      setNewComment('')
      toast.success('Đã thêm bình luận')
    } catch (error) {
      console.error('Error creating comment:', error)
      const errorMessage = error.response?.data?.message || 'Không thể thêm bình luận'
      toast.error(errorMessage)
    }
  }

  const handleStartEditComment = (comment) => {
    setEditingCommentId(comment.id)
    setEditingContent(comment.content)
  }

  const handleCancelEditComment = () => {
    setEditingCommentId(null)
    setEditingContent('')
  }

  const handleUpdateComment = async (commentId) => {
    if (!editingContent.trim()) return
    try {
      await commentAPI.updateComment(commentId, { content: editingContent })

      // Reload comments sau khi cập nhật
      const commentsData = await commentAPI.getComments(id)
      const normalizeComments = async (raw) => {
        if (!Array.isArray(raw)) return []

        const authorIds = Array.from(
          new Set(
            raw
              .map((c) => (typeof c.author === 'string' ? c.author : null))
              .filter((aid) => aid && aid !== 'anonymous')
          )
        )

        const profileMap = {}
        await Promise.allSettled(
          authorIds.map(async (authorId) => {
            try {
              if (
                user &&
                (authorId === user.id ||
                  authorId === user.userId ||
                  authorId === user._id)
              ) {
                profileMap[authorId] = user
                return
              }
              const profile = await userAPI.getUser(authorId)
              profileMap[authorId] = profile
            } catch (e) {
              console.warn('Failed to load author profile for', authorId, e)
            }
          })
        )

        return raw.map((c) => {
          let authorObj = c.author

          if (typeof c.author === 'string') {
            const authorId = c.author
            const profile = profileMap[authorId]

            if (profile) {
              authorObj = {
                id: profile.id || profile.userId || authorId,
                fullName: profile.fullName || 'Người dùng',
                avatar:
                  profile.avatar ||
                  'https://ui-avatars.com/api/?name=' +
                    encodeURIComponent(profile.fullName || 'User'),
              }
            } else if (
              user &&
              (authorId === user.id ||
                authorId === user.userId ||
                authorId === user._id)
            ) {
              authorObj = {
                id: user.id || user.userId || authorId,
                fullName: user.fullName || 'Bạn',
                avatar:
                  user.avatar ||
                  'https://ui-avatars.com/api/?name=' +
                    encodeURIComponent(user.fullName || 'User'),
              }
            } else {
              authorObj = {
                id: authorId,
                fullName: 'Người dùng',
                avatar: 'https://ui-avatars.com/api/?name=User',
              }
            }
          }

          return {
            id: c.id,
            content: c.content,
            images: c.images || [],
            createdAt: c.createdAt || c.created_at,
            author: authorObj,
          }
        })
      }

      const normalized = await normalizeComments(commentsData)
      setComments(normalized)
      setEditingCommentId(null)
      setEditingContent('')
      toast.success('Đã cập nhật bình luận')
    } catch (error) {
      console.error('Error updating comment:', error)
      toast.error('Không thể cập nhật bình luận')
    }
  }

  const handleDeleteComment = async (commentId) => {
    try {
      await commentAPI.deleteComment(commentId)
      setComments((prev) => prev.filter((c) => c.id !== commentId))
      toast.success('Đã xóa bình luận')
    } catch (error) {
      console.error('Error deleting comment:', error)
      toast.error('Không thể xóa bình luận')
    }
  }

  const handleSubmitRating = async () => {
    if (!isAuthenticated) {
      toast.error('Vui lòng đăng nhập để đánh giá')
      return
    }
    if (ratingValue === 0) return

    try {
      const payload = {
        rating: ratingValue,
        authorId: user?.id || user?.userId || user?._id,
      }

      if (myRating) {
        await ratingAPI.updateRating(id, payload)
      } else {
        await ratingAPI.createRating(id, payload)
      }

      // Cập nhật lại thống kê rating trên UI (average + count)
      setMyRating({ ...(myRating || {}), rating: ratingValue })
      setRatings((prev) => {
        const prevAvg = prev?.averageRating || 0
        const prevCount = prev?.totalRatings || 0

        let newAvg = prevAvg
        let newCount = prevCount

        if (myRating && typeof myRating.rating === 'number') {
          // User đã có rating trước đó: thay thế điểm cũ bằng điểm mới
          newCount = prevCount || 1
          newAvg =
            newCount === 0
              ? ratingValue
              : (prevAvg * newCount - myRating.rating + ratingValue) / newCount
        } else {
          // User rating lần đầu: tăng tổng số đánh giá lên 1
          newCount = prevCount + 1
          newAvg =
            newCount === 0
              ? ratingValue
              : (prevAvg * prevCount + ratingValue) / newCount
        }

        return { averageRating: newAvg, totalRatings: newCount }
      })

      toast.success('Đã gửi đánh giá')
    } catch (error) {
      toast.error('Không thể gửi đánh giá')
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!recipe) {
    return <div className="text-center py-12">Không tìm thấy công thức</div>
  }

  const formatCommentTime = (createdAt) => {
    if (!createdAt) return ''
    const date = new Date(createdAt)
    if (Number.isNaN(date.getTime())) {
      // Backend comment-service đang trả "18-12-2025 20:25:02" -> JS Date không parse được
      // Hiển thị raw string để tránh làm crash UI
      return createdAt
    }
    return formatDistanceToNow(date, { addSuffix: true })
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
              <Link to={`/users/${recipe.author.id}`} className="hover:text-primary-600">
                {recipe.author.fullName}
              </Link>
              <span>•</span>
              <span>{formatDistanceToNow(new Date(recipe.createdAt), { addSuffix: true })}</span>
            </div>
            <h1 className="text-3xl font-bold mb-4">{recipe.title}</h1>
            <p className="text-gray-600 mb-4">{recipe.description}</p>
            
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <span className="flex items-center text-gray-600">
                <FiClock className="mr-1" />
                {recipe.cookingTime} phút
              </span>
              <span className="flex items-center text-gray-600">
                <FiUsers className="mr-1" />
                {recipe.servings} người
              </span>
              <span className="flex items-center text-gray-600">
                <FiEye className="mr-1" />
                {recipe.viewsCount.toLocaleString()} lượt xem
              </span>
              <span className="flex items-center text-yellow-500">
                <FiStar className="fill-current mr-1" />
                {recipe.averageRating.toFixed(1)} ({recipe.ratingsCount})
              </span>
            </div>
          </div>

          {/* Images */}
          {recipe.images && recipe.images.length > 0 && (
            <div className="mb-8">
              <img
                src={recipe.images[0]}
                alt={recipe.title}
                className="w-full h-96 object-cover rounded-lg"
              />
            </div>
          )}

          {/* Ingredients */}
          <div className="card p-6 mb-6">
            <h2 className="text-2xl font-bold mb-4">Nguyên liệu</h2>
            <ul className="space-y-2">
              {recipe.ingredients?.map((ingredient, index) => (
                <li key={index} className="flex items-start">
                  <span className="mr-2">•</span>
                  <div>
                    <span className="font-medium">{ingredient.name}</span>
                    <span className="text-gray-600 ml-2">{ingredient.amount}</span>
                    {ingredient.note && (
                      <span className="text-gray-500 text-sm ml-2">({ingredient.note})</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Instructions */}
          <div className="card p-6 mb-6">
            <h2 className="text-2xl font-bold mb-4">Cách làm</h2>
            <div className="space-y-6">
              {recipe.instructions?.map((instruction, index) => (
                <div key={index} className="flex space-x-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
                    {instruction.step}
                  </div>
                  <div className="flex-1">
                    {instruction.image && (
                      <img
                        src={instruction.image}
                        alt={`Bước ${instruction.step}`}
                        className="w-full h-48 object-cover rounded-lg mb-2"
                      />
                    )}
                    <p className="text-gray-700">{instruction.description}</p>
                    {instruction.duration && (
                      <p className="text-sm text-gray-500 mt-1">
                        Thời gian: {instruction.duration} phút
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tips */}
          {recipe.tips && recipe.tips.length > 0 && (
            <div className="card p-6 mb-6 bg-yellow-50">
              <h2 className="text-2xl font-bold mb-4">💡 Mẹo nhỏ</h2>
              <ul className="space-y-2">
                {recipe.tips.map((tip, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Nutrition Info */}
          {recipe.nutritionInfo && (
            <div className="card p-6 mb-6">
              <h2 className="text-2xl font-bold mb-4">Thông tin dinh dưỡng</h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div>
                  <p className="text-gray-500 text-sm">Calories</p>
                  <p className="font-bold">{recipe.nutritionInfo.calories} kcal</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Protein</p>
                  <p className="font-bold">{recipe.nutritionInfo.protein}g</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Carbs</p>
                  <p className="font-bold">{recipe.nutritionInfo.carbs}g</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Fat</p>
                  <p className="font-bold">{recipe.nutritionInfo.fat}g</p>
                </div>
                <div>
                  <p className="text-gray-500 text-sm">Fiber</p>
                  <p className="font-bold">{recipe.nutritionInfo.fiber}g</p>
                </div>
              </div>
            </div>
          )}

          {/* Comments */}
          <div className="card p-6">
            <h2 className="text-2xl font-bold mb-4">
              Bình luận ({comments.length})
            </h2>
            
            {isAuthenticated && (
              <form onSubmit={handleSubmitComment} className="mb-6">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Viết bình luận..."
                  className="input-field w-full h-24 mb-2"
                  rows="3"
                />
                <button type="submit" className="btn-primary">
                  Gửi bình luận
                </button>
              </form>
            )}

            <div className="space-y-4">
              {comments.map((comment) => (
                <div key={comment.id} className="border-b border-gray-200 pb-4 last:border-0">
                  <div className="flex items-start space-x-3">
                    <img
                      src={comment.author?.avatar || 'https://ui-avatars.com/api/?name=User'}
                      alt={comment.author?.fullName || 'Người dùng'}
                      className="w-10 h-10 rounded-full"
                    />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium">{comment.author?.fullName || 'Người dùng'}</span>
                        <span className="text-sm text-gray-500">
                          {formatCommentTime(comment.createdAt)}
                        </span>
                      </div>
                      {editingCommentId === comment.id ? (
                        <div className="space-y-2 mt-1">
                          <textarea
                            className="input-field w-full h-20"
                            value={editingContent}
                            onChange={(e) => setEditingContent(e.target.value)}
                          />
                          <div className="flex space-x-2">
                            <button
                              type="button"
                              className="btn-primary"
                              onClick={() => handleUpdateComment(comment.id)}
                            >
                              Lưu
                            </button>
                            <button
                              type="button"
                              className="btn-secondary"
                              onClick={handleCancelEditComment}
                            >
                              Hủy
                            </button>
                          </div>
                        </div>
                      ) : (
                        <p className="text-gray-700">{comment.content}</p>
                      )}
                      {comment.images && comment.images.length > 0 && (
                        <div className="mt-2 flex space-x-2">
                          {comment.images.map((img, idx) => (
                            <img key={idx} src={img} alt="" className="w-20 h-20 object-cover rounded" />
                          ))}
                        </div>
                      )}

                      {isAuthenticated &&
                        user &&
                        (comment.author?.id === user.id ||
                          comment.author?.id === user.userId ||
                          comment.author?.id === user._id) && (
                          <div className="flex space-x-3 mt-2 text-sm">
                            <button
                              type="button"
                              className="text-primary-600 hover:underline"
                              onClick={() => handleStartEditComment(comment)}
                            >
                              Chỉnh sửa
                            </button>
                            <button
                              type="button"
                              className="text-red-600 hover:underline"
                              onClick={() => setCommentToDelete(comment)}
                            >
                              Xóa
                            </button>
                          </div>
                        )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          {/* Rating */}
          {isAuthenticated && (
            <div className="card p-6 mb-6">
              <h3 className="font-bold mb-4">Đánh giá của bạn</h3>
              <div className="flex items-center space-x-2 mb-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setRatingValue(star)}
                    className={`text-2xl ${
                      star <= ratingValue ? 'text-yellow-500' : 'text-gray-300'
                    }`}
                  >
                    ★
                  </button>
                ))}
              </div>
              <button onClick={handleSubmitRating} className="btn-primary w-full">
                Gửi đánh giá
              </button>
            </div>
          )}

          {/* Rating Stats */}
          {ratings && (
            <div className="card p-6 mb-6">
              <h3 className="font-bold mb-4">Đánh giá</h3>
              <div className="text-center mb-4">
                <div className="text-4xl font-bold text-primary-600">
                  {Number(ratings.averageRating || 0).toFixed(1)}
                </div>
                <div className="flex items-center justify-center space-x-1 text-yellow-500">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <FiStar
                      key={star}
                      className={star <= Math.round(ratings.averageRating) ? 'fill-current' : ''}
                    />
                  ))}
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  {ratings.totalRatings || 0} đánh giá
                </p>
              </div>
            </div>
          )}

          {/* Author Info */}
          <div className="card p-6">
            <Link to={`/users/${recipe.author.id}`} className="flex items-center space-x-3 mb-4">
              <img
                src={recipe.author.avatar}
                alt={recipe.author.fullName}
                className="w-16 h-16 rounded-full"
              />
              <div>
                <p className="font-bold">{recipe.author.fullName}</p>
                <p className="text-sm text-gray-500">@{recipe.author.username}</p>
              </div>
            </Link>
            <p className="text-sm text-gray-600 mb-4">{recipe.author.bio}</p>
            <div className="flex items-center justify-between text-sm">
              <span>{recipe.author.recipesCount} công thức</span>
              <span>{recipe.author.followersCount} người theo dõi</span>
            </div>
          </div>
        </div>
      </div>

      {commentToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-lg max-w-sm w-full p-6">
            <h3 className="text-lg font-semibold mb-2">Xác nhận xóa bình luận</h3>
            <p className="text-sm text-gray-700 mb-4">
              Bạn có chắc chắn muốn xóa bình luận này? Hành động này không thể hoàn tác.
            </p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setCommentToDelete(null)}
              >
                Hủy
              </button>
              <button
                type="button"
                className="btn-primary bg-orange-500 hover:bg-orange-600 border-orange-500"
                onClick={async () => {
                  const id = commentToDelete.id
                  setCommentToDelete(null)
                  await handleDeleteComment(id)
                }}
              >
                Xác nhận
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

