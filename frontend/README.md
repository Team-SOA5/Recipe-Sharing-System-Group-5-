# Cookpad-like Recipe Sharing Frontend

Frontend cho hệ thống chia sẻ công thức nấu ăn, được xây dựng bằng React.js và Vite.

## Tính năng

- ✅ Đăng ký / Đăng nhập
- ✅ Trang chủ với danh sách công thức
- ✅ Xem chi tiết công thức
- ✅ Tạo công thức mới
- ✅ Tìm kiếm công thức
- ✅ Xem profile người dùng
- ✅ Yêu thích công thức
- ✅ Đánh giá và bình luận
- ✅ Lọc theo danh mục, độ khó
- 🔄 Health Records (đang phát triển)
- 🔄 AI Recommendations (đang phát triển)

## Công nghệ sử dụng

- **React 18** - UI Framework
- **Vite** - Build tool
- **React Router** - Routing
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Hot Toast** - Notifications
- **React Icons** - Icons
- **date-fns** - Date formatting

## Cài đặt

```bash
cd frontend
npm install
```

## Chạy ứng dụng

```bash
npm run dev
```

Ứng dụng sẽ chạy tại `http://localhost:3000`

## Build cho production

```bash
npm run build
```

## Cấu trúc dự án

```
frontend/
├── src/
│   ├── components/      # Các components tái sử dụng
│   │   ├── Layout.jsx
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   ├── RecipeCard.jsx
│   │   └── ProtectedRoute.jsx
│   ├── contexts/        # React Context
│   │   └── AuthContext.jsx
│   ├── pages/           # Các trang
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── RecipeDetail.jsx
│   │   ├── RecipeCreate.jsx
│   │   ├── Search.jsx
│   │   ├── Profile.jsx
│   │   └── ...
│   ├── services/        # API services
│   │   ├── api.js       # API client (có thể chuyển sang backend thật)
│   │   └── mockData.js  # Mock data cho frontend độc lập
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
└── vite.config.js
```

## Mock Data Mode

Frontend hiện đang chạy ở chế độ **Mock Data** để có thể hoạt động độc lập không cần backend.

Để chuyển sang sử dụng backend thật:

1. Mở file `src/services/api.js`
2. Đổi `const USE_MOCK = true` thành `const USE_MOCK = false`
3. Đảm bảo backend đang chạy tại `http://localhost:8888`

## API Endpoints

Khi kết nối với backend, frontend sẽ gọi các API sau:

- `POST /api/v1/auth/login` - Đăng nhập
- `POST /api/v1/auth/register` - Đăng ký
- `GET /api/v1/recipes` - Lấy danh sách công thức
- `GET /api/v1/recipes/:id` - Lấy chi tiết công thức
- `POST /api/v1/recipes` - Tạo công thức mới
- `GET /api/v1/search/recipes` - Tìm kiếm công thức
- Và nhiều endpoints khác theo OpenAPI spec

Xem file `openapi.yaml` ở thư mục gốc để biết chi tiết đầy đủ.

## Ghi chú

- Tất cả dữ liệu hiện tại là mock data
- Authentication được mô phỏng với localStorage
- Khi có backend thật, chỉ cần đổi flag `USE_MOCK` trong `api.js`
- UI được thiết kế responsive, hỗ trợ mobile và desktop

## License

MIT

