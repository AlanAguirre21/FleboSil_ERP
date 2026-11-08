import { Fragment, isValidElement, type ReactNode } from 'react'

import {
  MENSAJE_SIN_COINCIDENCIAS,
  usePaginacion,
  type BusquedaControlada,
  type FilasPorPagina,
} from '../../hooks/usePaginacion'
import { BarraListado, PieListado } from './Paginacion'
import styles from './Tabla.module.css'

export interface ColumnaTabla<T> {
  clave: Extract<keyof T, string>
  // Texto, o un control (ej. la casilla "seleccionar todas" de Nóminas).
  encabezado: ReactNode
  render?: (fila: T) => ReactNode
  // 'derecha' para columnas numéricas o de dinero.
  alineacion?: 'derecha'
  // Texto con el que el buscador encuentra la fila por esta columna, cuando
  // lo que se ve no sale del propio `render` (ej. un componente sin texto).
  textoBusqueda?: (fila: T) => string
}

interface TablaProps<T> {
  columnas: ColumnaTabla<T>[]
  datos: T[]
  claveFila?: keyof T
  renderAcciones?: (fila: T) => ReactNode
  mensajeVacio?: string
  // Fila de totales opcional (ej. "Sumas" de un balance): una celda por
  // columna, con la misma alineación que su columna.
  filaPie?: ReactNode[]
  // Fila de detalle opcional bajo cada fila (ej. historial de un cliente):
  // si devuelve contenido, ocupa todo el ancho justo debajo de su fila.
  renderExpandido?: (fila: T) => ReactNode
  // `false` oculta el buscador (se conserva "Mostrar" y la paginación).
  buscador?: boolean
  // La pantalla guarda el texto y filtra `datos` con su propia lógica; el
  // buscador se sigue mostrando aquí, a la altura de "Mostrar".
  busquedaControlada?: BusquedaControlada
  placeholderBusqueda?: string
  filasPorPaginaInicial?: FilasPorPagina
}

// Texto visible de un nodo de React (cadenas, números y los hijos de los
// elementos), para que el buscador encuentre lo mismo que se ve en la celda.
function textoDeNodo(nodo: ReactNode): string {
  if (nodo == null || typeof nodo === 'boolean') return ''
  if (typeof nodo === 'string' || typeof nodo === 'number' || typeof nodo === 'bigint') return String(nodo)
  if (Array.isArray(nodo)) return nodo.map(textoDeNodo).join(' ')
  if (isValidElement<{ children?: ReactNode }>(nodo)) return textoDeNodo(nodo.props.children)
  return ''
}

function textoDeFila<T>(fila: T, columnas: ColumnaTabla<T>[]): string {
  return columnas
    .map((columna) => {
      const crudo = fila[columna.clave]
      return [
        columna.textoBusqueda?.(fila) ?? '',
        columna.render ? textoDeNodo(columna.render(fila)) : '',
        typeof crudo === 'string' || typeof crudo === 'number' ? String(crudo) : '',
      ].join(' ')
    })
    .join(' ')
}

export function Tabla<T>({
  columnas,
  datos,
  claveFila = 'id' as keyof T,
  renderAcciones,
  mensajeVacio = 'Sin datos para mostrar.',
  filaPie,
  renderExpandido,
  buscador = true,
  placeholderBusqueda = 'Buscar…',
  filasPorPaginaInicial = 10,
  busquedaControlada,
}: TablaProps<T>) {
  const paginacion = usePaginacion(
    datos,
    (fila) => textoDeFila(fila, columnas),
    filasPorPaginaInicial,
    busquedaControlada,
  )
  const { visibles } = paginacion
  const totalColumnas = columnas.length + (renderAcciones ? 1 : 0)
  const mensaje = datos.length > 0 && visibles.length === 0 ? MENSAJE_SIN_COINCIDENCIAS : mensajeVacio

  return (
    <div className={styles.tableWrapper}>
      <BarraListado estado={paginacion} buscador={buscador} placeholderBusqueda={placeholderBusqueda} />

      <div className={styles.tableContainer}>
        <table className="dataTable">
          <thead>
            <tr>
              {columnas.map((columna) => (
                <th key={columna.clave} className={columna.alineacion === 'derecha' ? 'numeric' : undefined}>
                  {columna.encabezado}
                </th>
              ))}
              {renderAcciones && <th>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {visibles.map((fila) => {
              const expandido = renderExpandido?.(fila)
              return (
                <Fragment key={String(fila[claveFila])}>
                  <tr>
                    {columnas.map((columna) => (
                      <td key={columna.clave} className={columna.alineacion === 'derecha' ? 'numeric' : undefined}>
                        {columna.render ? columna.render(fila) : (fila[columna.clave] as ReactNode)}
                      </td>
                    ))}
                    {renderAcciones && <td>{renderAcciones(fila)}</td>}
                  </tr>
                  {expandido != null && expandido !== false && (
                    <tr className="expandedRow">
                      <td colSpan={totalColumnas}>{expandido}</td>
                    </tr>
                  )}
                </Fragment>
              )
            })}
          </tbody>
          {filaPie && visibles.length > 0 && (
            <tfoot>
              <tr>
                {columnas.map((columna, indice) => (
                  <td key={columna.clave} className={columna.alineacion === 'derecha' ? 'numeric' : undefined}>
                    {filaPie[indice]}
                  </td>
                ))}
                {renderAcciones && <td />}
              </tr>
            </tfoot>
          )}
        </table>
        {visibles.length === 0 && <p className={styles.tableEmpty}>{mensaje}</p>}
      </div>

      <PieListado estado={paginacion} />
    </div>
  )
}
