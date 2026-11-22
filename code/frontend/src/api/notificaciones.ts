import { apiClient } from './client'

// Centro de notificaciones de la campana (001, "Actualización: centro de
// notificaciones y avisos por correo"). El backend ya recorta por rol.

export type ClaveSeccionNotificacion = 'stock' | 'ventas' | 'compras' | 'facturas' | 'nominas'

export interface ElementoNotificacion {
  titulo: string
  detalle: string
  // "Vencida · hace N días", "Error de timbrado", "Por cobrar $X"…
  etiqueta: string | null
  // Requiere acción (cuenta en el contador).
  urgente: boolean
  ruta: string
}

export interface SeccionNotificacion {
  clave: ClaveSeccionNotificacion
  titulo: string
  ruta: string
  total: number
  requieren_accion: number
  // Hasta 5, los más urgentes primero.
  elementos: ElementoNotificacion[]
}

export interface Notificaciones {
  // Solo lo que requiere acción.
  contador: number
  // Solo secciones con elementos.
  secciones: SeccionNotificacion[]
}

export async function getNotificaciones(): Promise<Notificaciones> {
  const { data } = await apiClient.get<Notificaciones>('/notificaciones/')
  return data
}
