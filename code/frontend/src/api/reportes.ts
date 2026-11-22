import { apiClient } from './client'
import type { EstadoFactura } from './facturacion'

// Fuera de "dia" (incluido "personalizado", con `desde`/`hasta`), solo el
// admin: el backend responde 403 al operador (016, "Actualización: periodos
// ampliados, comparación y producción").
export type PeriodoDashboard = 'dia' | 'semana' | 'mes' | 'año' | 'personalizado'

// Agrupación de las series; la elige el backend según el periodo o la
// duración del rango.
export type Granularidad = 'hora' | 'dia' | 'semana' | 'mes'

export interface ConsultaPeriodo {
  periodo: PeriodoDashboard
  // Solo con `periodo: 'personalizado'`, en formato AAAA-MM-DD.
  desde?: string
  hasta?: string
}

function parametrosPeriodo({ periodo, desde, hasta }: ConsultaPeriodo) {
  return periodo === 'personalizado' ? { periodo, desde, hasta } : { periodo }
}

// Parte de la clave de React Query que identifica el periodo consultado.
export function clavePeriodo({ periodo, desde, hasta }: ConsultaPeriodo) {
  return periodo === 'personalizado' ? [periodo, desde ?? null, hasta ?? null] : [periodo]
}

// Porcentaje con un decimal, o `null` si el periodo anterior es cero.
export type Variacion = string | null

// Fechas (hora local, ISO) del periodo anterior contra el que se compara.
export interface PeriodoAnterior {
  inicio: string
  fin: string
}

export interface PuntoResumenDashboard {
  fecha: string
  ganancia: string
}

// `ganancia`, `serie` y su comparación solo llegan al admin; el operador
// recibe los totales que usan Ventas y Compras (016, "Actualización:
// ganancias y movimientos de caja solo para admin").
export interface ResumenDashboard {
  periodo: PeriodoDashboard
  granularidad?: Granularidad
  ventas_total: string
  compras_total: string
  ganancia?: string
  serie?: PuntoResumenDashboard[]
  periodo_anterior?: PeriodoAnterior
  anterior: { ventas_total: string; compras_total: string; ganancia?: string }
  variacion: { ventas_total: Variacion; compras_total: Variacion; ganancia?: Variacion }
}

export async function getResumenDashboard(consulta: ConsultaPeriodo): Promise<ResumenDashboard> {
  const { data } = await apiClient.get<ResumenDashboard>('/reportes/resumen/', { params: parametrosPeriodo(consulta) })
  return data
}

export interface PuntoMonto {
  fecha: string
  monto: string
}

export interface ConteoEstado {
  tipo: string
  cantidad: number
}

export interface ResumenVentas {
  periodo: PeriodoDashboard
  granularidad: Granularidad
  con_envio: PuntoMonto[]
  sin_envio: PuntoMonto[]
  envio: PuntoMonto[]
  conteo_estado: ConteoEstado[]
  numero_ventas: number
  // `null` sin ventas en el periodo.
  ticket_promedio: string | null
  periodo_anterior: PeriodoAnterior
  anterior: { numero_ventas: number; ticket_promedio: string | null }
  variacion: { numero_ventas: Variacion; ticket_promedio: Variacion }
}

export async function getResumenVentas(consulta: ConsultaPeriodo): Promise<ResumenVentas> {
  const { data } = await apiClient.get<ResumenVentas>('/reportes/ventas/', { params: parametrosPeriodo(consulta) })
  return data
}

export interface ResumenCompras {
  periodo: PeriodoDashboard
  granularidad: Granularidad
  todas: PuntoMonto[]
  productos: PuntoMonto[]
  insumos: PuntoMonto[]
  conteo_estado: ConteoEstado[]
}

export async function getResumenCompras(consulta: ConsultaPeriodo): Promise<ResumenCompras> {
  const { data } = await apiClient.get<ResumenCompras>('/reportes/compras/', { params: parametrosPeriodo(consulta) })
  return data
}

export type OrdenTop = 'mas' | 'menos'

// "importe" es solo del admin.
export type CriterioTopProductos = 'cantidad' | 'importe'

// Por cantidad trae `cantidad`; por importe, `importe`.
export interface ProductoTop {
  producto: string
  cantidad?: string
  importe?: string
}

export async function getProductosTop(
  consulta: ConsultaPeriodo,
  orden: OrdenTop,
  por: CriterioTopProductos = 'cantidad',
): Promise<ProductoTop[]> {
  const { data } = await apiClient.get<ProductoTop[]>('/reportes/productos-top/', {
    params: { ...parametrosPeriodo(consulta), orden, por },
  })
  return data
}

// Admin: monto comprado. Operador: número de compras, sin importes.
export interface ClienteTop {
  cliente: string
  monto?: string
  compras?: number
}

export async function getClientesTop(consulta: ConsultaPeriodo, orden: OrdenTop): Promise<ClienteTop[]> {
  const { data } = await apiClient.get<ClienteTop[]>('/reportes/clientes-top/', {
    params: { ...parametrosPeriodo(consulta), orden },
  })
  return data
}

export type LimiteMovimientos = '5' | '10' | 'todos'

export interface MovimientoCajaReporte {
  fecha: string
  tipo_movimiento: 'ingreso' | 'retiro'
  observacion: string
}

export async function getMovimientosCajaReporte(
  consulta: ConsultaPeriodo,
  limite: LimiteMovimientos,
): Promise<MovimientoCajaReporte[]> {
  const { data } = await apiClient.get<MovimientoCajaReporte[]>('/reportes/movimientos-caja/', {
    params: { ...parametrosPeriodo(consulta), limite },
  })
  return data
}

// --- Resumen facturación (016, "Actualización: Resumen facturación con datos")

export interface PuntoFacturacion {
  fecha: string
  total: string
  pue: string
  ppd: string
}

export interface ConteoEstadoFactura {
  estado: EstadoFactura
  tipo: string
  cantidad: number
}

export interface FacturaPorAtender {
  id: number
  serie: string
  folio_interno: number | null
  cliente: string
  total: string
  estado: EstadoFactura
  fecha: string
}

export interface ResumenFacturacion {
  periodo: PeriodoDashboard
  granularidad: Granularidad
  facturado_total: string
  facturas_emitidas: number
  por_cobrar_ppd: string
  // `null` si no hay ventas en el periodo.
  porcentaje_facturado: string | null
  serie: PuntoFacturacion[]
  conteo_estado: ConteoEstadoFactura[]
  // Pendientes accionables (error / pendiente de cancelación): no dependen del periodo.
  requiere_atencion: FacturaPorAtender[]
  periodo_anterior: PeriodoAnterior
  anterior: { facturado_total: string }
  variacion: { facturado_total: Variacion }
}

export async function getResumenFacturacion(consulta: ConsultaPeriodo): Promise<ResumenFacturacion> {
  const { data } = await apiClient.get<ResumenFacturacion>('/reportes/facturacion/', {
    params: parametrosPeriodo(consulta),
  })
  return data
}

// --- Resumen producción (016, "Actualización: periodos ampliados, comparación y producción")

export interface PuntoUnidades {
  fecha: string
  unidades: string
}

export interface ProductoProducido {
  producto: string
  cantidad: string
}

export interface ResumenProduccion {
  periodo: PeriodoDashboard
  granularidad: Granularidad
  producciones: number
  unidades_producidas: string
  // Solo llega al admin.
  costo_total?: string
  serie: PuntoUnidades[]
  top_productos: ProductoProducido[]
}

export async function getResumenProduccion(consulta: ConsultaPeriodo): Promise<ResumenProduccion> {
  const { data } = await apiClient.get<ResumenProduccion>('/reportes/produccion/', {
    params: parametrosPeriodo(consulta),
  })
  return data
}
