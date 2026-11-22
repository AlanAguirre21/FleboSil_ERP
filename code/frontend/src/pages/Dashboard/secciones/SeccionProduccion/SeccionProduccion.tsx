import { useNavigate } from 'react-router-dom'

import type { ConsultaPeriodo } from '../../../../api/reportes'
import { BotonPrimario } from '../../../../components/common/BotonPrimario'
import { useResumenProduccion } from '../../../../hooks/useResumenProduccion'
import { formatearCantidad, formatearMoneda, mapearSerie } from '../../compartido/formato'
import { GraficaBarras } from '../../compartido/GraficaBarras'
import { GraficaLinea } from '../../compartido/GraficaLinea'
import styles from '../../compartido/SeccionOperacion.module.css'

// Sección "Resumen de producción" — `016`, "Actualización: periodos
// ampliados, comparación y producción". Toda la empresa para ambos roles,
// como el módulo Producción; el costo solo llega al admin.

interface SeccionProduccionProps {
  consulta: ConsultaPeriodo
  esAdmin: boolean
}

const formatearUnidades = (valor: number) => `${formatearCantidad(valor)} u.`

export function SeccionProduccion({ consulta, esAdmin }: SeccionProduccionProps) {
  const navigate = useNavigate()
  const { data: resumen, isLoading } = useResumenProduccion(consulta)

  const serie = mapearSerie(resumen?.serie, resumen?.granularidad, (punto) => Number(punto.unidades))
  // Sin producciones, la gráfica muestra su estado vacío en vez de una línea plana.
  const datosSerie = serie.some((punto) => punto.valor !== 0) ? serie : []
  const datosTop = (resumen?.top_productos ?? []).map((fila) => ({ etiqueta: fila.producto, valor: Number(fila.cantidad) }))

  return (
    <section className="card">
      <div className="sectionHeader">
        <h2 className="sectionTitle">Resumen de producción</h2>
        <div className="headerActions">
          <span className={styles.indicator}>
            <span className={styles.indicatorLabel}>Producciones</span>
            <span className={styles.indicatorAmount}>{resumen ? resumen.producciones : '…'}</span>
          </span>
          <span className={styles.indicator}>
            <span className={styles.indicatorLabel}>Unidades producidas</span>
            <span className={styles.indicatorAmount}>
              {resumen ? formatearCantidad(resumen.unidades_producidas) : '…'}
            </span>
          </span>
          {esAdmin && (
            <span className={styles.indicator}>
              <span className={styles.indicatorLabel}>Costo de producción</span>
              <span className={styles.indicatorAmount}>
                {resumen?.costo_total !== undefined ? formatearMoneda(resumen.costo_total) : '…'}
              </span>
            </span>
          )}
          <BotonPrimario variante="secundario" onClick={() => navigate('/produccion')}>
            Ir a Producción
          </BotonPrimario>
        </div>
      </div>

      {isLoading || !resumen ? (
        <p>Cargando resumen de producción…</p>
      ) : (
        <>
          <div className={styles.chartRowOne}>
            <GraficaLinea
              titulo="Unidades producidas"
              datos={datosSerie}
              color="var(--color-inicio)"
              formatoValor={formatearUnidades}
              etiquetaEjeY="Unidades"
            />
          </div>
          <div className={styles.chartRowOne}>
            <GraficaBarras
              titulo="Top 5 productos producidos"
              datos={datosTop}
              colores={['var(--color-inicio)']}
              etiquetaEjeY="Unidades"
              formatoValor={formatearUnidades}
            />
          </div>
        </>
      )}
    </section>
  )
}
