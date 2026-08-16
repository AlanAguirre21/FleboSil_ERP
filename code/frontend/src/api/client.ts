import axios from 'axios'

const TOKEN_KEY = 'flebosil_access_token'
const REFRESH_TOKEN_KEY = 'flebosil_refresh_token'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

apiClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refrescoEnCurso = null

function refrescarAccessToken() {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    return Promise.resolve(null)
  }

  if (!refrescoEnCurso) {
    refrescoEnCurso = axios
      .post(`${import.meta.env.VITE_API_URL}/token/refresh/`, { refresh: refreshToken })
      .then(({ data }) => {
        setToken(data.access)
        return data.access
      })
      .catch(() => {
        clearTokens()
        return null
      })
      .finally(() => {
        refrescoEnCurso = null
      })
  }

  return refrescoEnCurso
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const peticionOriginal = error.config

    if (error.response?.status === 401 && peticionOriginal && !peticionOriginal._reintentada) {
      peticionOriginal._reintentada = true
      const nuevoAccessToken = await refrescarAccessToken()
      if (nuevoAccessToken) {
        peticionOriginal.headers.Authorization = `Bearer ${nuevoAccessToken}`
        return apiClient(peticionOriginal)
      }
      clearTokens()
    }

    return Promise.reject(error)
  },
)

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setRefreshToken(token) {
  localStorage.setItem(REFRESH_TOKEN_KEY, token)
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}
