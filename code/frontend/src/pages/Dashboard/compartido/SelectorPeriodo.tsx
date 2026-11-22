import { useState, type FormEvent } from 'react'

import type { ConsultaPeriodo, PeriodoDashboard } from '../../../api/reportes'
import { AyudaInfo } from '../../../components/common/AyudaInfo'
import { BotonPrimario } from '../../../components/common/BotonPrimario'
import { describirPeriodo, formatearFechaCorta, hoyIso, primerDiaDelMesIso } from './formato'
import styles from './SelectorPeriodo.module.css'

const ETIQUETAS_PERIODO: { clave: PeriodoDashboard; etiqueta: string }[] = [
  { clave: 'dia', etiqueta: 'Día' },
  { clave: 'semana', etiqueta: 'Semana' },
  { clave: 'mes', etiqueta: 'Mes' },
  { clave: 'año', etiqueta: 'Año' },
  { clave: 'personalizado', etiqueta: 'Personalizado' },
]

interface SelectorPeriodoProps {
  periodos: PeriodoDashboard[]
  consulta: ConsultaPeriodo
  onCambiar: (consulta: ConsultaPeriodo) => void
  // Valida el rango con el backend y, si es válido, lo aplica. Devuelve el
  // mensaje de error o `null`.
  onAplicarRango: (desde: string, hasta: string) => Promise<string | null>
}

// Pestañas de periodo del Dashboard y, con "Personalizado", los campos del
// rango. El rango solo se aplica con "Aplicar", no con cada cambio.
export function SelectorPeriodo({ periodos, consulta, onCambiar, onAplicarRango }: SelectorPeriodoProps) {
  const [editandoRango, setEditandoRango] = useState(false)
  const [desde, setDesde] = useState(consulta.desde ?? primerDiaDelMesIso())
  const [hasta, setHasta] = useState(consulta.hasta ?? hoyIso())
  const [error, setError] = useState<string | null>(null)
  const [aplicando, setAplicando] = useState(false)

  const mostrarRango = editandoRango || consulta.periodo === 'personalizado'
  const pestañas = ETIQUETAS_PERIODO.filter((p) => periodos.includes(p.clave))

  const elegir = (periodo: PeriodoDashboard) => {
    setError(null)
    if (periodo === 'personalizado') {
      setEditandoRango(true)
      return
    }
    setEditandoRango(false)
    onCambiar({ periodo })
  }

  const aplicar = async (evento: FormEvent) => {
    evento.preventDefault()
    setAplicando(true)
    const mensaje = await onAplicarRango(desde, hasta)
    setAplicando(false)
    setError(mensaje)
    if (mensaje === null) setEditandoRango(false)
  }

  const activa = (periodo: PeriodoDashboard) =>
    periodo === 'personalizado' ? mostrarRango : !mostrarRango && consulta.periodo === periodo

  // Mientras se elige un rango nuevo, la ayuda describe ese rango (aún sin fechas).
  const periodoDescrito: ConsultaPeriodo =
    mostrarRango && consulta.periodo !== 'personalizado' ? { periodo: 'personalizado' } : consulta

  return (
    <div className={styles.periodSelector}>
      <div className={styles.periodRow}>
        <div className={styles.periodTabs} role="tablist" aria-label="Periodo">
          {pestañas.map((p) => (
            <button
              key={p.clave}
              type="button"
              role="tab"
              aria-selected={activa(p.clave)}
              className={activa(p.clave) ? `${styles.periodTab} ${styles.periodTabActive}` : styles.periodTab}
              onClick={() => elegir(p.clave)}
            >
              {p.etiqueta}
            </button>
          ))}
        </div>
        <AyudaInfo
          texto={describirPeriodo(periodoDescrito)}
          etiqueta="Qué fechas abarca el periodo"
          alineacion="derecha"
        />
      </div>

      {mostrarRango && (
        <form className={styles.rangeForm} onSubmit={aplicar} aria-label="Rango personalizado">
          <label className="filterField">
            Desde
            <input type="date" value={desde} max={hoyIso()} onChange={(e) => setDesde(e.target.value)} required />
          </label>
          <label className="filterField">
            Hasta
            <input type="date" value={hasta} max={hoyIso()} onChange={(e) => setHasta(e.target.value)} required />
          </label>
          <BotonPrimario type="submit" disabled={aplicando || !desde || !hasta}>
            {aplicando ? 'Aplicando…' : 'Aplicar'}
          </BotonPrimario>
        </form>
      )}

      {error && (
        <p className="errorMessage" role="alert">
          {error}
        </p>
      )}

      {consulta.periodo === 'personalizado' && consulta.desde && consulta.hasta && (
        <p className="pageHint">
          Del {formatearFechaCorta(consulta.desde)} al {formatearFechaCorta(consulta.hasta)}
        </p>
      )}
    </div>
  )
}
