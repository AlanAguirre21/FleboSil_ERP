import { useQuery } from '@tanstack/react-query'

import { clavePeriodo, getResumenVentas, type ConsultaPeriodo } from '../api/reportes'

export function useResumenVentas(consulta: ConsultaPeriodo) {
  return useQuery({
    queryKey: ['resumen-ventas', ...clavePeriodo(consulta)],
    queryFn: () => getResumenVentas(consulta),
    staleTime: 30_000,
  })
}
