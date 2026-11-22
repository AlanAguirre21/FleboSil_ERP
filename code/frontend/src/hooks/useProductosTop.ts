import { useQuery } from '@tanstack/react-query'

import {
  clavePeriodo,
  getProductosTop,
  type ConsultaPeriodo,
  type CriterioTopProductos,
  type OrdenTop,
} from '../api/reportes'

export function useProductosTop(consulta: ConsultaPeriodo, orden: OrdenTop, por: CriterioTopProductos = 'cantidad') {
  return useQuery({
    queryKey: ['productos-top', ...clavePeriodo(consulta), orden, por],
    queryFn: () => getProductosTop(consulta, orden, por),
    staleTime: 30_000,
  })
}
