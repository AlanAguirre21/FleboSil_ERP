import { useState } from 'react'

import type { ConsultaPeriodo, CriterioTopProductos, OrdenTop } from '../../../../api/reportes'
import { formatearMoneda } from '../../compartido/formato'
import { GraficaBarras } from '../../compartido/GraficaBarras'
import { useProductosTop } from '../../../../hooks/useProductosTop'

interface SeccionProductosProps {
  consulta: ConsultaPeriodo
  // Solo el admin puede ordenar por importe (el backend responde 403 al operador).
  esAdmin: boolean
}

const TITULOS: Record<CriterioTopProductos, Record<OrdenTop, string>> = {
  cantidad: { mas: 'Top 5 productos más vendidos', menos: 'Top 5 productos menos vendidos' },
  importe: { mas: 'Top 5 productos con mayor importe vendido', menos: 'Top 5 productos con menor importe vendido' },
}

function OpcionSegmentada({ activa, onClick, children }: { activa: boolean; onClick: () => void; children: string }) {
  return (
    <button
      type="button"
      className={activa ? 'segmentedOption segmentedOptionActive' : 'segmentedOption'}
      aria-pressed={activa}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

export function SeccionProductos({ consulta, esAdmin }: SeccionProductosProps) {
  const [orden, setOrden] = useState<OrdenTop>('mas')
  const [criterio, setCriterio] = useState<CriterioTopProductos>('cantidad')
  const por: CriterioTopProductos = esAdmin ? criterio : 'cantidad'
  const { data: productos, isLoading } = useProductosTop(consulta, orden, por)

  const datos = (productos ?? []).map((producto) => ({
    etiqueta: producto.producto,
    valor: Number(por === 'importe' ? (producto.importe ?? 0) : (producto.cantidad ?? 0)),
  }))

  return (
    <section className="card">
      <div className="sectionHeader">
        <h2 className="sectionTitle">Resumen de productos</h2>
        <div className="headerActions">
          {esAdmin && (
            <div className="segmented" role="group" aria-label="Criterio del ranking de productos">
              <OpcionSegmentada activa={por === 'cantidad'} onClick={() => setCriterio('cantidad')}>
                Unidades
              </OpcionSegmentada>
              <OpcionSegmentada activa={por === 'importe'} onClick={() => setCriterio('importe')}>
                Importe
              </OpcionSegmentada>
            </div>
          )}
          <div className="segmented" role="group" aria-label="Orden del ranking de productos">
            <OpcionSegmentada activa={orden === 'mas'} onClick={() => setOrden('mas')}>
              Más vendidos
            </OpcionSegmentada>
            <OpcionSegmentada activa={orden === 'menos'} onClick={() => setOrden('menos')}>
              Menos vendidos
            </OpcionSegmentada>
          </div>
        </div>
      </div>

      {isLoading ? (
        <p>Cargando productos…</p>
      ) : datos.length === 0 ? (
        <p className="emptyState">No hay ventas de productos en este periodo.</p>
      ) : (
        <GraficaBarras
          titulo={TITULOS[por][orden]}
          datos={datos}
          colores={['var(--color-primario)']}
          etiquetaEjeY={por === 'importe' ? 'Importe vendido ($)' : 'Cantidad vendida'}
          formatoValor={por === 'importe' ? formatearMoneda : undefined}
        />
      )}
    </section>
  )
}
