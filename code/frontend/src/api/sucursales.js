import { apiClient } from './client'

export async function getSucursales() {
  const { data } = await apiClient.get('/sucursales/')
  return data
}

export async function crearSucursal(datos) {
  const { data } = await apiClient.post('/sucursales/', datos)
  return data
}

export async function editarSucursal(id, datos) {
  const { data } = await apiClient.patch(`/sucursales/${id}/`, datos)
  return data
}

export async function desactivarSucursal(id) {
  await apiClient.delete(`/sucursales/${id}/`)
}
