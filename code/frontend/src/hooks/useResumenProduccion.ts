import { useQuery } from '@tanstack/react-query'

import { clavePeriodo, getResumenProduccion, type ConsultaPeriodo } from '../api/reportes'

export function useResumenProduccion(consulta: ConsultaPeriodo) {
  return useQuery({
    queryKey: ['resumen-produccion', ...clavePeriodo(consulta)],
    queryFn: () => getResumenProduccion(consulta),
    staleTime: 30_000,
  })
}
