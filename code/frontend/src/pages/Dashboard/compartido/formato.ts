import type { ConsultaPeriodo, Granularidad, PeriodoAnterior } from '../../../api/reportes'
import type { PuntoGrafica } from './GraficaLinea'

export function formatearMoneda(valor: string | number) {
  return `$${Number(valor).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

export function formatearCantidad(valor: string | number) {
  return Number(valor).toLocaleString('es-MX', { maximumFractionDigits: 2 })
}

interface ContextoSerie {
  // La serie abarca más de un día (rango personalizado agrupado por hora).
  variosDias?: boolean
  // La serie abarca más de un año (agrupación mensual).
  variosAnios?: boolean
}

// Las fechas del backend llegan en hora local ("2026-03-01T00:00:00-06:00"):
// los primeros caracteres son la fecha y el año locales.
function contextoDe(fechas: string[]): ContextoSerie {
  return {
    variosDias: new Set(fechas.map((fecha) => fecha.slice(0, 10))).size > 1,
    variosAnios: new Set(fechas.map((fecha) => fecha.slice(0, 4))).size > 1,
  }
}

const DIA_MES: Intl.DateTimeFormatOptions = { day: '2-digit', month: '2-digit' }

export function formatearEtiquetaFecha(fecha: string, granularidad: Granularidad, contexto: ContextoSerie = {}) {
  const valor = new Date(fecha)
  if (granularidad === 'hora') {
    const hora = valor.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
    return contexto.variosDias ? `${valor.toLocaleDateString('es-MX', DIA_MES)} ${hora}` : hora
  }
  if (granularidad === 'mes') {
    return valor.toLocaleDateString('es-MX', contexto.variosAnios ? { month: 'short', year: 'numeric' } : { month: 'short' })
  }
  if (granularidad === 'semana') {
    // Cada punto es una semana de lunes a domingo, rotulada con su lunes.
    return `Sem. ${valor.toLocaleDateString('es-MX', DIA_MES)}`
  }
  return valor.toLocaleDateString('es-MX', DIA_MES)
}

// Convierte una serie del backend en puntos de gráfica, con etiquetas según
// la agrupación que devolvió el backend.
export function mapearSerie<T extends { fecha: string }>(
  puntos: T[] | undefined,
  granularidad: Granularidad | undefined,
  valor: (punto: T) => number,
): PuntoGrafica[] {
  const lista = puntos ?? []
  const contexto = contextoDe(lista.map((punto) => punto.fecha))
  return lista.map((punto) => ({
    etiqueta: formatearEtiquetaFecha(punto.fecha, granularidad ?? 'dia', contexto),
    valor: valor(punto),
  }))
}

export function formatearFechaMovimiento(fecha: string) {
  return new Date(fecha).toLocaleString('es-MX', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// "AAAA-MM-DD" → "dd/mm/aaaa", sin pasar por `Date` (evita el corrimiento de
// un día que provoca interpretar la fecha como UTC).
export function formatearFechaCorta(fecha: string) {
  const [anio, mes, dia] = fecha.split('-')
  return `${dia}/${mes}/${anio}`
}

// Fecha local de hoy en formato AAAA-MM-DD (para los campos `type="date"`).
export function hoyIso(desplazamientoDias = 0, base = new Date()) {
  const fecha = new Date(base)
  fecha.setDate(fecha.getDate() + desplazamientoDias)
  const mes = String(fecha.getMonth() + 1).padStart(2, '0')
  const dia = String(fecha.getDate()).padStart(2, '0')
  return `${fecha.getFullYear()}-${mes}-${dia}`
}

export function primerDiaDelMesIso() {
  return `${hoyIso().slice(0, 8)}01`
}

// Texto breve de qué fechas abarca un periodo, para el icono de ayuda del
// selector. Los periodos de calendario van de su inicio a este momento.
export function describirPeriodo(consulta: ConsultaPeriodo, hoy = new Date()): string {
  const hoyLocal = hoyIso(0, hoy)
  switch (consulta.periodo) {
    case 'dia':
      return `Hoy (${formatearFechaCorta(hoyLocal)}), desde las 00:00 hasta ahora.`
    case 'semana':
      // Semanas de lunes a domingo, igual que el backend.
      return `Del lunes ${formatearFechaCorta(hoyIso(-((hoy.getDay() + 6) % 7), hoy))} a hoy.`
    case 'mes':
      return `Del ${formatearFechaCorta(`${hoyLocal.slice(0, 8)}01`)} a hoy.`
    case 'año':
      return `Del ${formatearFechaCorta(`${hoyLocal.slice(0, 4)}-01-01`)} a hoy.`
    case 'personalizado':
      return consulta.desde && consulta.hasta
        ? `Del ${formatearFechaCorta(consulta.desde)} al ${formatearFechaCorta(consulta.hasta)}, ambos incluidos.`
        : 'Elige las fechas y pulsa "Aplicar".'
  }
}

// Texto breve de las fechas contra las que se compara una variación. Las
// fechas llegan en hora local ("2026-11-21T10:30:00-06:00"), así que se leen
// por posición sin pasar por `Date`.
export function describirPeriodoAnterior({ inicio, fin }: PeriodoAnterior): string {
  const diaInicio = formatearFechaCorta(inicio.slice(0, 10))
  const diaFin = formatearFechaCorta(fin.slice(0, 10))
  const horaInicio = inicio.slice(11, 16)
  const horaFin = fin.slice(11, 16)
  const desdeMedianoche = horaInicio === '00:00'
  const hastaFinDelDia = horaFin === '23:59'

  if (diaInicio === diaFin) {
    return desdeMedianoche && hastaFinDelDia
      ? `Comparado con el ${diaInicio}.`
      : `Comparado con el ${diaInicio}, de ${horaInicio} a ${horaFin}.`
  }
  const desde = desdeMedianoche ? diaInicio : `${diaInicio} ${horaInicio}`
  const hasta = hastaFinDelDia ? '.' : `, hasta las ${horaFin}.`
  return `Comparado con el periodo del ${desde} al ${diaFin}${hasta}`
}
