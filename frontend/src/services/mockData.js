// Mock data để frontend có thể chạy độc lập
// Sau này sẽ thay thế bằng API calls thật

export const mockUsers = [
  {
    id: 'usr_001',
    username: 'chef_master',
    fullName: 'Nguyễn Văn A',
    avatar: 'https://i.pravatar.cc/150?img=1',
    bio: 'Đam mê nấu ăn và chia sẻ công thức',
    recipesCount: 45,
    followersCount: 1250,
    followingCount: 320,
    createdAt: '2023-01-15T00:00:00Z',
  },
  {
    id: 'usr_002',
    username: 'home_cook',
    fullName: 'Trần Thị B',
    avatar: 'https://i.pravatar.cc/150?img=2',
    bio: 'Nấu ăn tại nhà, yêu thích món Việt',
    recipesCount: 28,
    followersCount: 890,
    followingCount: 150,
    createdAt: '2023-03-20T00:00:00Z',
  },
]

export const mockCategories = [
  { id: 'cat_001', name: 'Món chính', description: 'Các món ăn chính', icon: '🍛', recipesCount: 1250 },
  { id: 'cat_002', name: 'Món canh', description: 'Các món canh, súp', icon: '🍲', recipesCount: 890 },
  { id: 'cat_003', name: 'Món tráng miệng', description: 'Bánh, chè, kem', icon: '🍰', recipesCount: 650 },
  { id: 'cat_004', name: 'Món chay', description: 'Các món ăn chay', icon: '🥗', recipesCount: 420 },
  { id: 'cat_005', name: 'Đồ uống', description: 'Nước ép, sinh tố', icon: '🥤', recipesCount: 380 },
]

export const mockTags = [
  { id: 'tag_001', name: 'healthy', recipesCount: 456 },
  { id: 'tag_002', name: 'traditional', recipesCount: 320 },
  { id: 'tag_003', name: 'vietnamese', recipesCount: 890 },
  { id: 'tag_004', name: 'easy', recipesCount: 650 },
  { id: 'tag_005', name: 'quick', recipesCount: 420 },
]

export const mockRecipes = [
  {
    id: 'rcp_001',
    title: 'Phở bò Hà Nội truyền thống',
    description: 'Công thức nấu phở bò chuẩn vị Hà Nội, thơm ngon đậm đà',
    thumbnail: 'https://images.unsplash.com/photo-1529016922-330022d9bbaa?w=800',
    author: mockUsers[0],
    category: mockCategories[0],
    difficulty: 'medium',
    cookingTime: 120,
    servings: 4,
    averageRating: 4.8,
    ratingsCount: 256,
    viewsCount: 12500,
    favoritesCount: 890,
    commentsCount: 45,
    tags: [mockTags[1], mockTags[2]],
    createdAt: '2024-01-15T00:00:00Z',
    updatedAt: '2024-01-15T00:00:00Z',
    isFavorited: false,
  },
  {
    id: 'rcp_002',
    title: 'Bánh mì thịt nướng',
    description: 'Bánh mì giòn tan với thịt nướng thơm lừng',
    thumbnail: 'https://images.unsplash.com/photo-1571115764595-644a1f56a55c?w=800',
    author: mockUsers[1],
    category: mockCategories[0],
    difficulty: 'easy',
    cookingTime: 30,
    servings: 2,
    averageRating: 4.6,
    ratingsCount: 189,
    viewsCount: 8900,
    favoritesCount: 650,
    commentsCount: 32,
    tags: [mockTags[2], mockTags[3]],
    createdAt: '2024-02-10T00:00:00Z',
    updatedAt: '2024-02-10T00:00:00Z',
    isFavorited: true,
  },
  {
    id: 'rcp_003',
    title: 'Chè đậu xanh',
    description: 'Chè đậu xanh mát lạnh, ngọt thanh',
    thumbnail: 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=800',
    author: mockUsers[0],
    category: mockCategories[2],
    difficulty: 'easy',
    cookingTime: 45,
    servings: 6,
    averageRating: 4.7,
    ratingsCount: 145,
    viewsCount: 5600,
    favoritesCount: 420,
    commentsCount: 28,
    tags: [mockTags[0], mockTags[3]],
    createdAt: '2024-03-05T00:00:00Z',
    updatedAt: '2024-03-05T00:00:00Z',
    isFavorited: false,
  },
  {
    id: 'rcp_004',
    title: 'Canh chua cá lóc',
    description: 'Canh chua chua ngọt, cá tươi ngon',
    thumbnail: 'https://images.unsplash.com/photo-1559339352-11d03503665b?w=800',
    author: mockUsers[1],
    category: mockCategories[1],
    difficulty: 'medium',
    cookingTime: 60,
    servings: 4,
    averageRating: 4.9,
    ratingsCount: 312,
    viewsCount: 15200,
    favoritesCount: 1100,
    commentsCount: 67,
    tags: [mockTags[2], mockTags[4]],
    createdAt: '2024-01-20T00:00:00Z',
    updatedAt: '2024-01-20T00:00:00Z',
    isFavorited: true,
  },
  {
    id: 'rcp_005',
    title: 'Gỏi cuốn tôm thịt',
    description: 'Gỏi cuốn tươi ngon, thanh mát',
    thumbnail: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800',
    author: mockUsers[0],
    category: mockCategories[0],
    difficulty: 'easy',
    cookingTime: 25,
    servings: 4,
    averageRating: 4.5,
    ratingsCount: 198,
    viewsCount: 7800,
    favoritesCount: 580,
    commentsCount: 41,
    tags: [mockTags[0], mockTags[3], mockTags[4]],
    createdAt: '2024-02-25T00:00:00Z',
    updatedAt: '2024-02-25T00:00:00Z',
    isFavorited: false,
  },
  {
    id: 'rcp_006',
    title: 'Bún chả Hà Nội',
    description: 'Bún chả đậm đà, thơm ngon',
    thumbnail: 'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=800',
    author: mockUsers[1],
    category: mockCategories[0],
    difficulty: 'medium',
    cookingTime: 90,
    servings: 4,
    averageRating: 4.8,
    ratingsCount: 267,
    viewsCount: 13400,
    favoritesCount: 950,
    commentsCount: 52,
    tags: [mockTags[1], mockTags[2]],
    createdAt: '2024-01-30T00:00:00Z',
    updatedAt: '2024-01-30T00:00:00Z',
    isFavorited: true,
  },
]

export const mockRecipeDetail = {
  ...mockRecipes[0],
  ingredients: [
    { name: 'Thịt bò', amount: '500g', note: 'Chọn phần nạc vai' },
    { name: 'Xương bò', amount: '1kg', note: 'Xương ống' },
    { name: 'Bánh phở', amount: '500g', note: 'Phở tươi' },
    { name: 'Hành tây', amount: '2 củ', note: '' },
    { name: 'Gừng', amount: '1 củ', note: '' },
    { name: 'Quế', amount: '2 thanh', note: '' },
    { name: 'Hoa hồi', amount: '3 cánh', note: '' },
    { name: 'Gia vị', amount: 'Vừa đủ', note: 'Muối, đường, nước mắm' },
  ],
  instructions: [
    {
      step: 1,
      description: 'Luộc xương bò với gừng trong 10 phút để loại bỏ mùi hôi',
      image: 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400',
      duration: 10,
    },
    {
      step: 2,
      description: 'Rửa sạch xương, cho vào nồi lớn với 3 lít nước, đun sôi',
      image: 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400',
      duration: 15,
    },
    {
      step: 3,
      description: 'Thêm quế, hoa hồi, hành tây vào nồi, hầm nhỏ lửa trong 2 giờ',
      image: 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400',
      duration: 120,
    },
    {
      step: 4,
      description: 'Nêm nếm gia vị cho vừa ăn, nước dùng phải trong và ngọt',
      image: 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400',
      duration: 5,
    },
    {
      step: 5,
      description: 'Thái thịt bò mỏng, trần qua nước sôi',
      image: 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400',
      duration: 3,
    },
    {
      step: 6,
      description: 'Trần bánh phở, xếp thịt bò lên, chan nước dùng nóng',
      image: 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400',
      duration: 2,
    },
  ],
  images: [
    'https://images.unsplash.com/photo-1529016922-330022d9bbaa?w=800',
    'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=800',
  ],
  nutritionInfo: {
    calories: 450,
    protein: 25.5,
    carbs: 60.2,
    fat: 12.8,
    fiber: 3.5,
  },
  tips: [
    'Xương bò nên luộc sơ để nước phở trong',
    'Gia vị nêm nếm từ từ để vừa khẩu vị',
    'Nước dùng phải hầm đủ lâu để ngọt tự nhiên',
  ],
}

export const mockComments = [
  {
    id: 'cmt_001',
    content: 'Món này rất ngon! Cảm ơn bạn đã chia sẻ',
    author: mockUsers[1],
    images: [],
    likesCount: 15,
    isLiked: false,
    createdAt: '2024-01-16T10:00:00Z',
    updatedAt: '2024-01-16T10:00:00Z',
  },
  {
    id: 'cmt_002',
    content: 'Tôi đã làm theo và thành công rồi! Rất dễ làm',
    author: mockUsers[0],
    images: ['https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400'],
    likesCount: 8,
    isLiked: true,
    createdAt: '2024-01-17T14:30:00Z',
    updatedAt: '2024-01-17T14:30:00Z',
  },
]

export const mockRatings = {
  averageRating: 4.8,
  totalRatings: 256,
  distribution: {
    5: 180,
    4: 50,
    3: 15,
    2: 8,
    1: 3,
  },
}

// Mock API responses với delay để giống thật
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

export const mockAPI = {
  // Auth
  login: async (email, password) => {
    await delay(800)
    if (email && password) {
      return {
        message: 'Thành công',
        accessToken: 'mock_token_' + Date.now(),
        refreshToken: 'mock_refresh_token',
      }
    }
    throw new Error('Email hoặc mật khẩu không đúng')
  },

  register: async (data) => {
    await delay(1000)
    return {
      message: 'Thành công',
      user: {
        ...mockUsers[0],
        email: data.email,
        username: data.username,
      },
    }
  },

  getCurrentUser: async () => {
    await delay(500)
    return {
      ...mockUsers[0],
      email: 'user@example.com',
      location: 'Hà Nội, Việt Nam',
      website: 'https://myblog.com',
      isFollowing: false,
    }
  },

  // Recipes
  getRecipes: async (params = {}) => {
    await delay(600)
    let recipes = [...mockRecipes]
    
    // Filter by category
    if (params.categoryId) {
      recipes = recipes.filter(r => r.category.id === params.categoryId)
    }
    
    // Filter by difficulty
    if (params.difficulty) {
      recipes = recipes.filter(r => r.difficulty === params.difficulty)
    }
    
    // Sort
    if (params.sort === 'most_viewed') {
      recipes.sort((a, b) => b.viewsCount - a.viewsCount)
    } else if (params.sort === 'most_liked') {
      recipes.sort((a, b) => b.favoritesCount - a.favoritesCount)
    } else if (params.sort === 'trending') {
      recipes.sort((a, b) => b.viewsCount + b.favoritesCount - (a.viewsCount + a.favoritesCount))
    }
    
    const page = params.page || 1
    const limit = params.limit || 20
    const start = (page - 1) * limit
    const end = start + limit
    
    return {
      data: recipes.slice(start, end),
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(recipes.length / limit),
        totalItems: recipes.length,
        itemsPerPage: limit,
        hasNextPage: end < recipes.length,
        hasPreviousPage: page > 1,
      },
    }
  },

  getRecipe: async (id) => {
    await delay(500)
    const recipe = mockRecipes.find(r => r.id === id)
    if (!recipe) throw new Error('Không tìm thấy công thức')
    return { ...mockRecipeDetail, ...recipe }
  },

  // Categories
  getCategories: async () => {
    await delay(300)
    return { data: mockCategories }
  },

  // Tags
  getPopularTags: async (limit = 20) => {
    await delay(300)
    return { data: mockTags.slice(0, limit) }
  },

  // Comments
  getComments: async (recipeId, params = {}) => {
    await delay(400)
    return {
      data: mockComments,
      pagination: {
        currentPage: 1,
        totalPages: 1,
        totalItems: mockComments.length,
        itemsPerPage: 20,
        hasNextPage: false,
        hasPreviousPage: false,
      },
    }
  },

  // Ratings
  getRatings: async (recipeId) => {
    await delay(300)
    return mockRatings
  },

  // Search
  searchRecipes: async (params) => {
    await delay(500)
    const query = params.q?.toLowerCase() || ''
    let results = mockRecipes.filter(r => 
      r.title.toLowerCase().includes(query) ||
      r.description.toLowerCase().includes(query)
    )
    
    return {
      data: results,
      pagination: {
        currentPage: 1,
        totalPages: 1,
        totalItems: results.length,
        itemsPerPage: 20,
        hasNextPage: false,
        hasPreviousPage: false,
      },
      filters: params,
    }
  },

  // User
  getUser: async (userId) => {
    await delay(400)
    const user = mockUsers.find(u => u.id === userId)
    if (!user) throw new Error('Không tìm thấy người dùng')
    return {
      ...user,
      email: 'user@example.com',
      location: 'Hà Nội, Việt Nam',
      isFollowing: false,
    }
  },

  getUserRecipes: async (userId, params = {}) => {
    await delay(500)
    const userRecipes = mockRecipes.filter(r => r.author.id === userId)
    return {
      data: userRecipes,
      pagination: {
        currentPage: 1,
        totalPages: 1,
        totalItems: userRecipes.length,
        itemsPerPage: 20,
        hasNextPage: false,
        hasPreviousPage: false,
      },
    }
  },
}

