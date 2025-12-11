import { Link } from 'react-router-dom'
import { FiClock, FiUsers, FiStar, FiEye, FiHeart } from 'react-icons/fi'
import { formatDistanceToNow } from 'date-fns'

export default function RecipeCard({ recipe }) {
  const difficultyColors = {
    easy: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    hard: 'bg-red-100 text-red-800',
  }

  const difficultyLabels = {
    easy: 'Dễ',
    medium: 'Trung bình',
    hard: 'Khó',
  }

  return (
    <Link to={`/recipes/${recipe.id}`} className="card hover:shadow-xl transition-shadow">
      <div className="relative">
        <img
          src={recipe.thumbnail}
          alt={recipe.title}
          className="w-full h-48 object-cover"
        />
        <div className="absolute top-2 right-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${difficultyColors[recipe.difficulty]}`}>
            {difficultyLabels[recipe.difficulty]}
          </span>
        </div>
        {recipe.isFavorited && (
          <div className="absolute top-2 left-2">
            <FiHeart className="text-red-500 fill-current" size={20} />
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2 line-clamp-2">{recipe.title}</h3>
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{recipe.description}</p>
        
        <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
          <div className="flex items-center space-x-4">
            <span className="flex items-center">
              <FiClock className="mr-1" />
              {recipe.cookingTime} phút
            </span>
            <span className="flex items-center">
              <FiUsers className="mr-1" />
              {recipe.servings} người
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <img
              src={recipe.author.avatar}
              alt={recipe.author.fullName}
              className="w-6 h-6 rounded-full"
            />
            <span className="text-sm text-gray-700">{recipe.author.fullName}</span>
          </div>
          <div className="flex items-center space-x-1 text-yellow-500">
            <FiStar className="fill-current" size={16} />
            <span className="text-sm font-medium">{recipe.averageRating.toFixed(1)}</span>
          </div>
        </div>

        <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-200">
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <span className="flex items-center">
              <FiEye className="mr-1" />
              {recipe.viewsCount.toLocaleString()}
            </span>
            <span className="flex items-center">
              <FiHeart className="mr-1" />
              {recipe.favoritesCount}
            </span>
          </div>
          <span className="text-xs text-gray-500">
            {formatDistanceToNow(new Date(recipe.createdAt), { addSuffix: true })}
          </span>
        </div>
      </div>
    </Link>
  )
}

