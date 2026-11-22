import { describe, expect, it } from 'vitest'

import { describirPeriodo, describirPeriodoAnterior, formatearFechaCorta, mapearSerie } from './formato'

const etiquetas = (fechas: string[], granularidad: 'hora' | 'dia' | 'semana' | 'mes') =>
  mapearSerie(fechas.map((fecha) => ({ fecha })), granularidad, () => 0).map((punto) => punto.etiqueta)

// Fechas en hora local del navegador (sin zona) para no depender de la del equipo de pruebas.
describe('etiquetas del eje X según la agrupación del backend', () => {
  it('por hora muestra solo la hora si la serie es de un día', () => {
    const [primera] = etiquetas(['2026-03-10T14:00:00', '2026-03-10T15:00:00'], 'hora')
    expect(primera).toMatch(/(14|02):00/)
    expect(primera).not.toMatch(/10\/03/)
  })

  it('por hora agrega el día si la serie abarca varios días', () => {
    expect(etiquetas(['2026-03-10T23:00:00', '2026-03-11T00:00:00'], 'hora')[1]).toMatch(/^11\/03 /)
  })

  it('por semana rotula con el lunes', () => {
    expect(etiquetas(['2026-03-09T00:00:00'], 'semana')).toEqual(['Sem. 09/03'])
  })

  it('por mes agrega el año solo si la serie cruza de año', () => {
    expect(etiquetas(['2026-01-01T00:00:00', '2026-02-01T00:00:00'], 'mes')[0]).not.toMatch(/2026/)
    expect(etiquetas(['2025-12-01T00:00:00', '2026-01-01T00:00:00'], 'mes')[1]).toMatch(/2026/)
  })

  it('formatea "AAAA-MM-DD" como dd/mm/aaaa', () => {
    expect(formatearFechaCorta('2026-03-01')).toBe('01/03/2026')
  })
})

describe('describirPeriodo', () => {
  // Domingo 22 de noviembre de 2026, hora local.
  const hoy = new Date(2026, 10, 22, 10, 30)

  it('describe cada periodo de calendario de su inicio a hoy', () => {
    expect(describirPeriodo({ periodo: 'dia' }, hoy)).toBe('Hoy (22/11/2026), desde las 00:00 hasta ahora.')
    expect(describirPeriodo({ periodo: 'semana' }, hoy)).toBe('Del lunes 16/11/2026 a hoy.')
    expect(describirPeriodo({ periodo: 'mes' }, hoy)).toBe('Del 01/11/2026 a hoy.')
    expect(describirPeriodo({ periodo: 'año' }, hoy)).toBe('Del 01/01/2026 a hoy.')
  })

  it('el lunes la semana empieza ese mismo día', () => {
    expect(describirPeriodo({ periodo: 'semana' }, new Date(2026, 10, 16, 8))).toBe('Del lunes 16/11/2026 a hoy.')
  })

  it('describe el rango personalizado aplicado', () => {
    expect(describirPeriodo({ periodo: 'personalizado', desde: '2026-03-01', hasta: '2026-03-15' }, hoy)).toBe(
      'Del 01/03/2026 al 15/03/2026, ambos incluidos.',
    )
  })
})

describe('describirPeriodoAnterior', () => {
  it('mismo día hasta la misma hora', () => {
    expect(describirPeriodoAnterior({ inicio: '2026-11-21T00:00:00-06:00', fin: '2026-11-21T10:30:00-06:00' })).toBe(
      'Comparado con el 21/11/2026, de 00:00 a 10:30.',
    )
  })

  it('varios días hasta la misma hora', () => {
    expect(describirPeriodoAnterior({ inicio: '2026-11-09T00:00:00-06:00', fin: '2026-11-15T10:30:00-06:00' })).toBe(
      'Comparado con el periodo del 09/11/2026 al 15/11/2026, hasta las 10:30.',
    )
  })

  it('días completos de un rango personalizado', () => {
    expect(
      describirPeriodoAnterior({ inicio: '2026-02-14T00:00:00-06:00', fin: '2026-02-28T23:59:59.999999-06:00' }),
    ).toBe('Comparado con el periodo del 14/02/2026 al 28/02/2026.')
  })
})
