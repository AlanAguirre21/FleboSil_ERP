import { apiClient } from './client'

export async function login(email, password) {
  const { data } = await apiClient.post('/auth/login/', { email, password })
  return data
}

export async function solicitarRecuperacion(email) {
  const { data } = await apiClient.post('/auth/recuperar/', { email })
  return data
}

export async function verificarCodigo(email, codigo) {
  const { data } = await apiClient.post('/auth/verificar-codigo/', { email, codigo })
  return data
}

export async function cambiarContrasena(email, password, passwordConfirmacion) {
  const { data } = await apiClient.post('/auth/cambiar-contrasena/', {
    email,
    password,
    password_confirmacion: passwordConfirmacion,
  })
  return data
}
