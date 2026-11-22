import { useQuery } from '@tanstack/react-query'

import {
  clavePeriodo,
  getMovimientosCajaReporte,
  type ConsultaPeriodo,
  type LimiteMovimientos,
} from '../api/reportes'

export function useMovimientosCajaDashboard(consulta: ConsultaPeriodo, limite: LimiteMovimientos) {
  return useQuery({
    queryKey: ['movimientos-caja-dashboard', ...clavePeriodo(consulta), limite],
    queryFn: () => getMovimientosCajaReporte(consulta, limite),
    staleTime: 30_000,
  })
}
