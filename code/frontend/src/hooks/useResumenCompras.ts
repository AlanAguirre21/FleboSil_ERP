import { useQuery } from '@tanstack/react-query'

import { clavePeriodo, getResumenCompras, type ConsultaPeriodo } from '../api/reportes'

export function useResumenCompras(consulta: ConsultaPeriodo) {
  return useQuery({
    queryKey: ['resumen-compras', ...clavePeriodo(consulta)],
    queryFn: () => getResumenCompras(consulta),
    staleTime: 30_000,
  })
}
