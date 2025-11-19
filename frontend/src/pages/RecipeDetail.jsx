import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { recipeAPI, commentAPI, ratingAPI } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { FiClock, FiUsers, FiStar, FiEye, FiHeart, FiMessageCircle, FiShare2 } from 'react-icons/fi'
import { formatDistanceToNow } from 'date-fns'
import toast from 'react-hot-toast'

export default function RecipeDetail() {
  const { id } = useParams()
  const { isAuthenticated } = useAuth()
  const [recipe, setRecipe] = useState(null)
  const [comments, setComments] = useState([])
  const [ratings, setRatings] = useState(null)
  const [myRating, setMyRating] = useState(null)
  const [loading, setLoading] = useState(true)
  const [newComment, setNewComment] = useState('')
  const [ratingValue, setRatingValue] = useState(0)

  useEffect(() => {
    loadRecipe()
  }, [id])

  const loadRecipe = async () => {
    try {
      setLoading(true)
      const [recipeData, commentsData, ratingsData] = await Promise.all([
        recipeAPI.getRecipe(id),
        commentAPI.getComments(id),
        ratingAPI.getRatings(id),
      ])
      setRecipe(recipeData)
      setComments(commentsData.data || [])
      setRatings(ratingsData)
      
      if (isAuthenticated) {
        try {
          const myRatingData = await ratingAPI.getMyRating(id)
          setMyRating(myRatingData)
          setRatingValue(myRatingData.rating)
        } catch (error) {
          // Chưa có rating
        }
      }
      
      // Increment view
      recipeAPI.incrementView(id).catch(console.error)
    } catch (error) {
      toast.error('Không thể tải công thức')
      console.error(error)
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
      const comment = await commentAPI.createComment(id, { content: newComment })
      setComments([comment, ...comments])
      setNewComment('')
      toast.success('Đã thêm bình luận')
    } catch (error) {
      toast.error('Không thể thêm bình luận')
    }
  }

  const handleSubmitRating = async () => {
    if (!isAuthenticated) {
      toast.error('Vui lòng đăng nhập để đánh giá')
      return
    }
    if (ratingValue === 0) return

    try {
      if (myRating) {
        await ratingAPI.updateRating(id, { rating: ratingValue })
      } else {
        await ratingAPI.createRating(id, { rating: ratingValue })
      }
      toast.success('Đã gửi đánh giá')
      loadRecipe()
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
                      src={comment.author.avatar}
                      alt={comment.author.fullName}
                      className="w-10 h-10 rounded-full"
                    />
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium">{comment.author.fullName}</span>
                        <span className="text-sm text-gray-500">
                          {formatDistanceToNow(new Date(comment.createdAt), { addSuffix: true })}
                        </span>
                      </div>
                      <p className="text-gray-700">{comment.content}</p>
                      {comment.images && comment.images.length > 0 && (
                        <div className="mt-2 flex space-x-2">
                          {comment.images.map((img, idx) => (
                            <img key={idx} src={img} alt="" className="w-20 h-20 object-cover rounded" />
                          ))}
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
                  {ratings.averageRating.toFixed(1)}
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
                  {ratings.totalRatings} đánh giá
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
    </div>
  )
}

