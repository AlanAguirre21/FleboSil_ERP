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

// --- Stock -----------------------------------------------------------

export type TipoItemInventario = 'producto' | 'materia_prima'

export interface StockItem {
  id: number
  nombre: string
  stock_actual: string
  stock_minimo: string
  stock_bajo: boolean
}

export async function getStock(tipo: TipoItemInventario, sucursalId: number): Promise<StockItem[]> {
  const { data } = await apiClient.get<StockItem[]>('/inventario/stock/', {
    params: { tipo, sucursal: sucursalId },
  })
  return data
}

// Ajuste manual de una fila (admin u operador; 011, "Actualización — ajuste de
// inventario…"). El stock contado se registra como un movimiento "Ajuste" por
// la diferencia; el mínimo, sin movimiento.
export type MotivoAjusteInventario = 'conteo_fisico' | 'merma' | 'caducidad' | 'correccion' | 'otro'

export const ETIQUETAS_MOTIVO_AJUSTE: Record<MotivoAjusteInventario, string> = {
  conteo_fisico: 'Conteo físico',
  merma: 'Merma o daño',
  caducidad: 'Caducidad',
  correccion: 'Corrección de captura',
  otro: 'Otro',
}

export interface AjusteInventarioPayload {
  tipo: TipoItemInventario
  sucursal: number
  item_id: number
  // Los cuatro siguientes solo cuando cambia el stock actual.
  stock_actual?: string
  // Lo que el usuario tenía en pantalla: si el stock cambió, el backend rechaza.
  stock_actual_visto?: string
  motivo_ajuste?: MotivoAjusteInventario
  nota?: string
  stock_minimo?: string
}

export async function ajustarInventario(datos: AjusteInventarioPayload): Promise<StockItem> {
  const { data } = await apiClient.post<StockItem>('/inventario/ajustes/', datos)
  return data
}

// --- Movimientos de inventario -------------------------------------------

export type TipoMovimientoInventario = 'entrada' | 'salida'
export type MotivoMovimientoInventario =
  | 'compra'
  | 'venta'
  | 'produccion_consumo'
  | 'produccion_entrada'
  | 'ajuste'
  | 'traslado_salida'
  | 'traslado_entrada'

// `traslado` es un valor agrupado del filtro (salida + entrada), no un motivo real.
export type FiltroMotivoMovimientoInventario = MotivoMovimientoInventario | 'traslado'

export interface MovimientoInventario {
  id: number
  fecha: string
  sucursal: number
  sucursal_nombre: string
  tipo_item: TipoItemInventario
  item_id: number
  item_nombre: string
  tipo_movimiento: TipoMovimientoInventario
  cantidad: string
  motivo: MotivoMovimientoInventario
  referencia_id: number | null
  stock_resultante: string
  usuario: number
  usuario_nombre: string
  // Solo en filas de traslado: la otra sucursal (destino si es salida, origen si es entrada).
  sucursal_contraparte: string | null
  // Motivo y nota de un ajuste manual ("Merma o daño: …"); vacío en los demás.
  observacion: string
}

export interface FiltrosMovimientosInventario {
  sucursal?: number
  tipo_item?: TipoItemInventario
  item_id?: number
  tipo_movimiento?: TipoMovimientoInventario
  motivo?: FiltroMotivoMovimientoInventario
}

export async function getMovimientosInventario(
  filtros: FiltrosMovimientosInventario,
): Promise<MovimientoInventario[]> {
  const { data } = await apiClient.get<MovimientoInventario[]>('/inventario/movimientos/', {
    params: filtros,
  })
  return data
}

// --- Traslados -------------------------------------------------------------

export interface LineaTrasladoPayload {
  tipo_item: TipoItemInventario
  item_id: number
  // `string` para no perder precisión decimal en el envío.
  cantidad: string
}

export interface CrearTrasladoPayload {
  sucursal_origen: number
  sucursal_destino: number
  detalles: LineaTrasladoPayload[]
}

export interface DetalleTraslado {
  id: number
  tipo_item: TipoItemInventario
  item_id: number
  item_nombre: string
  cantidad: string
}

export interface Traslado {
  id: number
  fecha: string
  sucursal_origen: number
  sucursal_origen_nombre: string
  sucursal_destino: number
  sucursal_destino_nombre: string
  usuario: number
  usuario_nombre: string
  detalles: DetalleTraslado[]
}

export async function crearTraslado(datos: CrearTrasladoPayload): Promise<Traslado> {
  const { data } = await apiClient.post<Traslado>('/inventario/traslados/', datos)
  return data
}
