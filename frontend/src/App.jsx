import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import RecipeDetail from './pages/RecipeDetail'
import RecipeCreate from './pages/RecipeCreate'
import RecipeEdit from './pages/RecipeEdit'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import UserProfile from './pages/UserProfile'
import Search from './pages/Search'
import Favorites from './pages/Favorites'
import HealthRecords from './pages/HealthRecords'
import AIRecommendations from './pages/AIRecommendations'
import MyRecipes from './pages/MyRecipes'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="recipes/:id" element={<RecipeDetail />} />
            <Route path="search" element={<Search />} />
            <Route path="users/:userId" element={<UserProfile />} />
            <Route
              path="recipes/create"
              element={
                <ProtectedRoute>
                  <RecipeCreate />
                </ProtectedRoute>
              }
            />
            <Route
              path="recipes/:id/edit"
              element={
                <ProtectedRoute>
                  <RecipeEdit />
                </ProtectedRoute>
              }
            />
            <Route
              path="profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="my-recipes"
              element={
                <ProtectedRoute>
                  <MyRecipes />
                </ProtectedRoute>
              }
            />
            <Route
              path="favorites"
              element={
                <ProtectedRoute>
                  <Favorites />
                </ProtectedRoute>
              }
            />
            <Route
              path="health"
              element={
                <ProtectedRoute>
                  <HealthRecords />
                </ProtectedRoute>
              }
            />
            <Route
              path="ai-recommendations"
              element={
                <ProtectedRoute>
                  <AIRecommendations />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
        <Toaster position="top-right" />
      </Router>
    </AuthProvider>
  )
}

export default App


