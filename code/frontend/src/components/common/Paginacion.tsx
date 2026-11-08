import {
  OPCIONES_FILAS_POR_PAGINA,
  paginasVisibles,
  type EstadoPaginacion,
  type FilasPorPagina,
} from '../../hooks/usePaginacion'
import styles from './Paginacion.module.css'

// Controles de un listado paginado (buscador, filas por página, conteo y
// botones de página). El estado vive en `usePaginacion`; los usa `Tabla` y
// también los listados que no son tabla (ej. pólizas del Libro diario).

interface BarraProps<T> {
  estado: EstadoPaginacion<T>
  buscador?: boolean
  placeholderBusqueda?: string
}

// Barra superior: buscador a la izquierda, filas por página a la derecha.
export function BarraListado<T>({ estado, buscador = true, placeholderBusqueda = 'Buscar…' }: BarraProps<T>) {
  // Con una búsqueda escrita se queda visible aunque no haya resultados, para poder borrarla.
  if (estado.totalDatos === 0 && !estado.busqueda) return null
  return (
    <div className={styles.listToolbar}>
      {buscador ? (
        <input
          type="search"
          className={styles.listSearch}
          placeholder={placeholderBusqueda}
          aria-label="Buscar en la tabla"
          value={estado.busqueda}
          onChange={(e) => estado.setBusqueda(e.target.value)}
        />
      ) : (
        <span />
      )}
      <label className={styles.listPageSize}>
        Mostrar
        <select
          aria-label="Filas por página"
          value={String(estado.filasPorPagina)}
          onChange={(e) =>
            estado.setFilasPorPagina(e.target.value === 'todas' ? 'todas' : (Number(e.target.value) as FilasPorPagina))
          }
        >
          {OPCIONES_FILAS_POR_PAGINA.map((opcion) => (
            <option key={opcion} value={String(opcion)}>
              {opcion === 'todas' ? 'Todas' : opcion}
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}

// Pie: "Mostrando X–Y de Z" y los botones de página.
export function PieListado<T>({ estado }: { estado: EstadoPaginacion<T> }) {
  const { totalFiltrados, totalDatos, inicio, visibles, pagina, totalPaginas, setPagina } = estado
  if (totalFiltrados === 0) return null
  return (
    <div className={styles.listFooter}>
      <span className={styles.listCount}>
        Mostrando {inicio + 1}–{inicio + visibles.length} de {totalFiltrados}
        {totalFiltrados !== totalDatos ? ` (de ${totalDatos} en total)` : ''}
      </span>
      {totalPaginas > 1 && (
        <nav className={styles.pagination} aria-label="Paginación">
          <button
            type="button"
            className={styles.pageButton}
            disabled={pagina === 1}
            onClick={() => setPagina(pagina - 1)}
          >
            Anterior
          </button>
          {paginasVisibles(pagina, totalPaginas).map((numero, indice) =>
            numero === null ? (
              <span key={`hueco-${indice}`} className={styles.pageGap}>
                …
              </span>
            ) : (
              <button
                key={numero}
                type="button"
                className={numero === pagina ? `${styles.pageButton} ${styles.pageButtonActive}` : styles.pageButton}
                aria-current={numero === pagina ? 'page' : undefined}
                aria-label={`Página ${numero}`}
                onClick={() => setPagina(numero)}
              >
                {numero}
              </button>
            ),
          )}
          <button
            type="button"
            className={styles.pageButton}
            disabled={pagina === totalPaginas}
            onClick={() => setPagina(pagina + 1)}
          >
            Siguiente
          </button>
        </nav>
      )}
    </div>
  )
}
