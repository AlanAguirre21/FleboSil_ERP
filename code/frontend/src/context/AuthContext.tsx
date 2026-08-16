import { useQueryClient } from '@tanstack/react-query'
import { createContext, useCallback, useContext, useMemo, useState } from 'react'

import { login as loginRequest } from '../api/auth'
import { clearTokens, getToken, setRefreshToken, setToken } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [autenticado, setAutenticado] = useState(() => Boolean(getToken()))
  const queryClient = useQueryClient()

  const login = useCallback(async (email, password) => {
    const { access, refresh } = await loginRequest(email, password)
    setToken(access)
    setRefreshToken(refresh)
    setAutenticado(true)
  }, [])

  // Guarda tokens ya emitidos por el backend (ej. tras cambiar contraseña
  // en la feature 005), sin volver a llamar al endpoint de login.
  const iniciarSesionConTokens = useCallback((access, refresh) => {
    setToken(access)
    setRefreshToken(refresh)
    setAutenticado(true)
  }, [])

  const logout = useCallback(() => {
    clearTokens()
    setAutenticado(false)
    queryClient.clear()
  }, [queryClient])

  const value = useMemo(
    () => ({ autenticado, login, logout, iniciarSesionConTokens }),
    [autenticado, login, logout, iniciarSesionConTokens],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components -- hook de conveniencia junto a su Provider, patrón estándar de contexto de React
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider')
  }
  return context
}
