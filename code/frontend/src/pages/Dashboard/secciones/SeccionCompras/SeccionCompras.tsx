import { useNavigate } from 'react-router-dom'

import type { ConsultaPeriodo, PuntoMonto } from '../../../../api/reportes'
import { BotonPrimario } from '../../../../components/common/BotonPrimario'
import { formatearMoneda, mapearSerie } from '../../compartido/formato'
import { GraficaBarras } from '../../compartido/GraficaBarras'
import { GraficaLinea } from '../../compartido/GraficaLinea'
import { Variacion } from '../../compartido/Variacion'
import { useResumenCompras } from '../../../../hooks/useResumenCompras'
import { useResumenDashboard } from '../../../../hooks/useResumenDashboard'
import styles from '../../compartido/SeccionOperacion.module.css'

interface SeccionComprasProps {
  consulta: ConsultaPeriodo
}

export function SeccionCompras({ consulta }: SeccionComprasProps) {
  const navigate = useNavigate()
  const { data: resumen, isLoading } = useResumenCompras(consulta)
  const { data: resumenGeneral } = useResumenDashboard(consulta)

  const mapear = (puntos?: PuntoMonto[]) => mapearSerie(puntos, resumen?.granularidad, (punto) => Number(punto.monto))

  const datosConteo = (resumen?.conteo_estado ?? []).map((fila) => ({ etiqueta: fila.tipo, valor: fila.cantidad }))

  return (
    <section className="card">
      <div className="sectionHeader">
        <h2 className="sectionTitle">Resumen de compras</h2>
        <div className="headerActions">
          <span className={styles.indicator}>
            <span className={styles.indicatorLabel}>Gasto en compras</span>
            <span className={styles.indicatorAmount}>
              {resumenGeneral ? formatearMoneda(resumenGeneral.compras_total) : '…'}
            </span>
            {/* Neutro: gastar más no es bueno ni malo por sí mismo. */}
            <Variacion
              valor={resumenGeneral?.variacion?.compras_total}
              periodoAnterior={resumenGeneral?.periodo_anterior}
              alineacion="derecha"
              neutral
            />
          </span>
          <BotonPrimario variante="secundario" onClick={() => navigate('/compras/nueva')}>
            Nueva compra
          </BotonPrimario>
        </div>
      </div>

      {isLoading || !resumen ? (
        <p>Cargando resumen de compras…</p>
      ) : (
        <>
          <div className={styles.chartRowThree}>
            <GraficaLinea titulo="Todas las compras" datos={mapear(resumen.todas)} color="var(--color-primario)" />
            <GraficaLinea titulo="Compras de productos" datos={mapear(resumen.productos)} color="var(--color-secundario)" />
            <GraficaLinea titulo="Compras de insumos" datos={mapear(resumen.insumos)} color="var(--color-inicio)" />
          </div>
          <div className={styles.chartRowOne}>
            <GraficaBarras
              titulo="Compras pendientes y recibidas"
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
