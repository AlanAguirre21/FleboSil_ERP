import { useQuery } from '@tanstack/react-query'

import { clavePeriodo, getResumenFacturacion, type ConsultaPeriodo } from '../api/reportes'

export function useResumenFacturacion(consulta: ConsultaPeriodo) {
  return useQuery({
    queryKey: ['resumen-facturacion', ...clavePeriodo(consulta)],
    queryFn: () => getResumenFacturacion(consulta),
    staleTime: 30_000,
  })
}
