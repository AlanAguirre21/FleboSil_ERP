import { apiClient } from './client'

export async function getUsuarioActual() {
  const { data } = await apiClient.get('/usuarios/me/')
  return data
}
