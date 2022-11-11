import { useAuthStore } from "../stores/auth.store"

export default function authHeader(url) {
    const { user } = useAuthStore()
    const isLoggedIn = !!user?.access_token
    const isApiUrl = url.startsWith(import.meta.env.VITE_API_URL)
  
    if (isLoggedIn && isApiUrl) {
      return { Authorization: 'Bearer ' + user.access_token }
    } else {
      return {}
    }
  }
  