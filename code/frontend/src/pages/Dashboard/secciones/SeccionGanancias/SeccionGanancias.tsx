import { useState } from 'react'

import type { ConsultaPeriodo, LimiteMovimientos } from '../../../../api/reportes'
import { AyudaInfo } from '../../../../components/common/AyudaInfo'
import { formatearFechaMovimiento, formatearMoneda, mapearSerie } from '../../compartido/formato'
import { GraficaLinea } from '../../compartido/GraficaLinea'
import { Variacion } from '../../compartido/Variacion'
import { useMovimientosCajaDashboard } from '../../../../hooks/useMovimientosCajaDashboard'
import { useResumenDashboard } from '../../../../hooks/useResumenDashboard'
import styles from './SeccionGanancias.module.css'

interface SeccionGananciasProps {
  consulta: ConsultaPeriodo
}

const OPCIONES_LIMITE: { valor: LimiteMovimientos; etiqueta: string }[] = [
  { valor: '5', etiqueta: '5' },
  { valor: '10', etiqueta: '10' },
  { valor: 'todos', etiqueta: 'Todos' },
]

const ETIQUETA_TIPO: Record<string, string> = { ingreso: 'Ingreso', retiro: 'Retiro' }

const AYUDA_GANANCIA = 'Ventas menos compras del periodo.'

export function SeccionGanancias({ consulta }: SeccionGananciasProps) {
  const { data: resumen, isLoading } = useResumenDashboard(consulta)
  const [limite, setLimite] = useState<LimiteMovimientos>('5')
  const { data: movimientos, isLoading: cargandoMovimientos } = useMovimientosCajaDashboard(consulta, limite)

  const datosGrafica = mapearSerie(resumen?.serie, resumen?.granularidad, (punto) => Number(punto.ganancia))

  const sinDatos = !isLoading && resumen && Number(resumen.ventas_total) === 0 && Number(resumen.compras_total) === 0

  return (
    <section className="card">
      <h2 className="sectionTitle">Ganancias del periodo</h2>

      <div className={styles.profitLayout}>
        <div className={styles.profitMain}>
          <div
            className={`${styles.profitCard} ${
              resumen && Number(resumen.ganancia) < 0 ? styles.profitNegative : styles.profitPositive
            }`}
          >
            <span className={styles.profitLabelRow}>
              <span className={styles.profitLabel}>Ganancia del periodo</span>
              <AyudaInfo texto={AYUDA_GANANCIA} etiqueta="Qué es la ganancia del periodo" />
            </span>
            <span className={styles.profitAmount}>{isLoading || resumen?.ganancia === undefined ? '…' : formatearMoneda(resumen.ganancia)}</span>
            <Variacion valor={resumen?.variacion?.ganancia} periodoAnterior={resumen?.periodo_anterior} />
          </div>

          {isLoading || !resumen ? (
            <p>Cargando resumen…</p>
          ) : sinDatos ? (
            <div className="placeholderBox">
              <span className="placeholderTitle">Todavía no hay suficientes datos para este periodo</span>
              <span>Registra una venta o compra para empezar a ver aquí la evolución de ganancias.</span>
            </div>
          ) : (
            <GraficaLinea titulo="Evolución de ganancia" datos={datosGrafica} color="var(--color-primario)" />
          )}
        </div>

        <div className={styles.movements}>
          <div className="sectionHeader">
            <h3 className="subtitle">Movimientos financieros del periodo</h3>
            <div className="segmented" role="group" aria-label="Cantidad de movimientos a mostrar">
              {OPCIONES_LIMITE.map((opcion) => (
                <button
                  key={opcion.valor}
                  type="button"
                  className={
                    limite === opcion.valor ? 'segmentedOption segmentedOptionActive' : 'segmentedOption'
                  }
                  aria-pressed={limite === opcion.valor}
                  onClick={() => setLimite(opcion.valor)}
                >
                  {opcion.etiqueta}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.movementListContainer}>
            <div className={styles.movementListContent}>
              {cargandoMovimientos || !movimientos ? (
                <p className={styles.movementListMessage}>Cargando movimientos…</p>
              ) : movimientos.length === 0 ? (
                <p className={styles.movementListMessage}>No hay movimientos de caja en este periodo.</p>
              ) : (
                <ul className={styles.movementList}>
                  {movimientos.map((movimiento, indice) => (
                    <li key={`${movimiento.fecha}-${indice}`} className={styles.movementRow}>
                      <span className={styles.movementDate}>{formatearFechaMovimiento(movimiento.fecha)}</span>
                      <span
                        className={
                          movimiento.tipo_movimiento === 'ingreso'
                            ? 'textSuccess'
                            : 'textError'
                        }
                      >
                        {ETIQUETA_TIPO[movimiento.tipo_movimiento]}
                      </span>
                      <span className={styles.movementDescription}>{movimiento.observacion}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
