import { useState } from 'react'

// Búsqueda, filas por página y paginación en pantalla de un listado (los
// controles visuales están en `components/common/Paginacion.tsx`).

export const OPCIONES_FILAS_POR_PAGINA = [10, 25, 50, 100, 'todas'] as const
export type FilasPorPagina = (typeof OPCIONES_FILAS_POR_PAGINA)[number]

// Minúsculas y sin acentos: "jose" encuentra "José".
export function normalizarBusqueda(texto: string): string {
  return texto.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim()
}

// Números de página a mostrar: siempre la primera y la última, y dos a cada
// lado de la actual; los huecos se marcan con `null` (puntos suspensivos).
// Un hueco de una sola página muestra ese número en vez de "…".
export function paginasVisibles(actual: number, total: number): (number | null)[] {
  const mostrar = (pagina: number) => pagina === 1 || pagina === total || Math.abs(pagina - actual) <= 2
  const paginas: (number | null)[] = []
  for (let pagina = 1; pagina <= total; pagina++) {
    if (mostrar(pagina) || (mostrar(pagina - 1) && mostrar(pagina + 1))) {
      paginas.push(pagina)
    } else if (paginas[paginas.length - 1] !== null) {
      paginas.push(null)
    }
  }
  return paginas
}

// Búsqueda cuyo texto guarda la pantalla (que además filtra la lista con su
// propia lógica, ej. por RFC aunque no sea columna): el buscador se muestra
// junto a "Mostrar", pero aquí no se vuelve a filtrar.
export interface BusquedaControlada {
  valor: string
  onCambiar: (valor: string) => void
  // Total antes de los filtros de la pantalla, para "Mostrando 1–4 de 4 (de 5 en total)".
  total?: number
}

export function usePaginacion<T>(
  datos: T[],
  textoDeFila: (fila: T) => string,
  filasIniciales: FilasPorPagina = 10,
  busquedaControlada?: BusquedaControlada,
) {
  const [busquedaPropia, setBusquedaPropia] = useState('')
  const [filasPorPagina, setFilasPorPaginaEstado] = useState<FilasPorPagina>(filasIniciales)
  const [pagina, setPagina] = useState(1)

  const busqueda = busquedaControlada ? busquedaControlada.valor : busquedaPropia
  const termino = busquedaControlada ? '' : normalizarBusqueda(busqueda)
  // Solo se arma el texto de cada fila cuando hay algo que buscar.
  const filtrados = termino ? datos.filter((fila) => normalizarBusqueda(textoDeFila(fila)).includes(termino)) : datos

  const tamano = filasPorPagina === 'todas' ? Math.max(filtrados.length, 1) : filasPorPagina
  const totalPaginas = Math.max(1, Math.ceil(filtrados.length / tamano))
  // Si los datos cambian (ej. otro filtro de la pantalla) y la página ya no
  // existe, se muestra la última que sí existe.
  const paginaActual = Math.min(pagina, totalPaginas)
  const inicio = (paginaActual - 1) * tamano
  const visibles = filtrados.slice(inicio, inicio + tamano)

  return {
    busqueda,
    setBusqueda: (valor: string) => {
      if (busquedaControlada) busquedaControlada.onCambiar(valor)
      else setBusquedaPropia(valor)
      setPagina(1)
    },
    filasPorPagina,
    setFilasPorPagina: (valor: FilasPorPagina) => {
      setFilasPorPaginaEstado(valor)
      setPagina(1)
    },
    pagina: paginaActual,
    setPagina,
    totalPaginas,
    inicio,
    visibles,
    totalFiltrados: filtrados.length,
    totalDatos: busquedaControlada?.total ?? datos.length,
  }
}

export type EstadoPaginacion<T> = ReturnType<typeof usePaginacion<T>>

// Mensaje para un listado con datos pero sin coincidencias de búsqueda.
export const MENSAJE_SIN_COINCIDENCIAS = 'Ninguna fila coincide con la búsqueda.'
