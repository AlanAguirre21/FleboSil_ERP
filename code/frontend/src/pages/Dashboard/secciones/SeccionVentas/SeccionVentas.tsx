import { useNavigate } from 'react-router-dom'

import type { ConsultaPeriodo, PuntoMonto } from '../../../../api/reportes'
import { AyudaInfo } from '../../../../components/common/AyudaInfo'
import { BotonPrimario } from '../../../../components/common/BotonPrimario'
import { formatearMoneda, mapearSerie } from '../../compartido/formato'
import { GraficaBarras } from '../../compartido/GraficaBarras'
import { GraficaLinea } from '../../compartido/GraficaLinea'
import { Variacion } from '../../compartido/Variacion'
import { useResumenDashboard } from '../../../../hooks/useResumenDashboard'
import { useResumenVentas } from '../../../../hooks/useResumenVentas'
import styles from '../../compartido/SeccionOperacion.module.css'

interface SeccionVentasProps {
  consulta: ConsultaPeriodo
}

const AYUDA_GANANCIA_VENTAS = 'Total vendido en el periodo, incluido el envío.'

export function SeccionVentas({ consulta }: SeccionVentasProps) {
  const navigate = useNavigate()
  const { data: resumen, isLoading } = useResumenVentas(consulta)
  const { data: resumenGeneral } = useResumenDashboard(consulta)

  const mapear = (puntos?: PuntoMonto[]) => mapearSerie(puntos, resumen?.granularidad, (punto) => Number(punto.monto))

  const datosConteo = (resumen?.conteo_estado ?? []).map((fila) => ({ etiqueta: fila.tipo, valor: fila.cantidad }))

  return (
    <section className="card">
      <div className="sectionHeader">
        <h2 className="sectionTitle">Resumen de ventas</h2>
        <div className="headerActions">
          <span className={styles.indicator}>
            <span className={styles.indicatorLabelRow}>
              <span className={styles.indicatorLabel}>Ganancia de ventas</span>
              <AyudaInfo texto={AYUDA_GANANCIA_VENTAS} etiqueta="Qué es la ganancia de ventas" alineacion="derecha" />
            </span>
            <span className={styles.indicatorAmount}>
              {resumenGeneral ? formatearMoneda(resumenGeneral.ventas_total) : '…'}
            </span>
            <Variacion
              valor={resumenGeneral?.variacion?.ventas_total}
              periodoAnterior={resumenGeneral?.periodo_anterior}
              alineacion="derecha"
            />
          </span>
          <span className={styles.indicator}>
            <span className={styles.indicatorLabel}>Número de ventas</span>
            <span className={styles.indicatorAmount}>{resumen ? resumen.numero_ventas : '…'}</span>
            <Variacion
              valor={resumen?.variacion?.numero_ventas}
              periodoAnterior={resumen?.periodo_anterior}
              alineacion="derecha"
            />
          </span>
          <span className={styles.indicator}>
            <span className={styles.indicatorLabel}>Ticket promedio</span>
            <span className={styles.indicatorAmount}>
              {!resumen ? '…' : resumen.ticket_promedio === null ? '—' : formatearMoneda(resumen.ticket_promedio)}
            </span>
            <Variacion
              valor={resumen?.variacion?.ticket_promedio}
              periodoAnterior={resumen?.periodo_anterior}
              alineacion="derecha"
            />
          </span>
          <BotonPrimario onClick={() => navigate('/ventas/nueva')}>Nueva venta</BotonPrimario>
        </div>
      </div>

      {isLoading || !resumen ? (
        <p>Cargando resumen de ventas…</p>
      ) : (
        <>
          <div className={styles.chartRowThree}>
            <GraficaLinea titulo="Ventas con envío" datos={mapear(resumen.con_envio)} color="var(--color-primario)" />
            <GraficaLinea titulo="Ventas sin envío" datos={mapear(resumen.sin_envio)} color="var(--color-secundario)" />
            <GraficaLinea titulo="Costo de envío" datos={mapear(resumen.envio)} color="var(--color-inicio)" />
          </div>
          <div className={styles.chartRowOne}>
            <GraficaBarras
              titulo="Ventas pendientes y entregadas"
              datos={datosConteo}
              colores={['var(--color-advertencia)', 'var(--color-exito)']}
              etiquetaEjeY="Cantidad"
            />
          </div>
        </>
      )}
    </section>
  )
}
