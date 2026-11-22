import { useQuery } from '@tanstack/react-query'

import { clavePeriodo, getClientesTop, type ConsultaPeriodo, type OrdenTop } from '../api/reportes'

export function useClientesTop(consulta: ConsultaPeriodo, orden: OrdenTop) {
  return useQuery({
    queryKey: ['clientes-top', ...clavePeriodo(consulta), orden],
    queryFn: () => getClientesTop(consulta, orden),
    staleTime: 30_000,
  })
}
