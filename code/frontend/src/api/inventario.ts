import { apiClient } from './client'

export async function getAlertasStock() {
  const { data } = await apiClient.get('/inventario/alertas/')
  return data
}
