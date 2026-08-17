import { apiClient } from './client'

export interface ModuloMenu {
  slug: string
  nombre: string
  ruta: string
}

export interface Usuario {
  nombre: string
  rol: 'admin' | 'operador'
  modulos: ModuloMenu[]
}

export async function getUsuarioActual(): Promise<Usuario> {
  const { data } = await apiClient.get<Usuario>('/usuarios/me/')
  return data
}
