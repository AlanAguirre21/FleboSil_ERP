import { apiClient } from './client'

export interface AlertaStock {
  tipo: 'producto' | 'materia_prima'
  nombre: string
  sucursal: string
  stock_actual: number | string
  stock_minimo: number | string
}

export async function getAlertasStock(): Promise<AlertaStock[]> {
  const { data } = await apiClient.get<AlertaStock[]>('/inventario/alertas/')
  return data
}
