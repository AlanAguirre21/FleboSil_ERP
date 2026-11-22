import { useQuery, useQueryClient } from '@tanstack/react-query'

import { clavePeriodo, getResumenDashboard, type ConsultaPeriodo } from '../api/reportes'

function opcionesResumenDashboard(consulta: ConsultaPeriodo) {
  return {
    queryKey: ['resumen-dashboard', ...clavePeriodo(consulta)],
    queryFn: () => getResumenDashboard(consulta),
    // Corto a propósito (a diferencia de módulos más estáticos como
    // Catálogo/Sucursales): el dashboard debe reflejar una venta/compra
    // recién registrada al volver a esta pantalla, sin recarga manual.
    staleTime: 30_000,
  }
}

export function useResumenDashboard(consulta: ConsultaPeriodo) {
  return useQuery(opcionesResumenDashboard(consulta))
}

// Pide el resumen de un periodo antes de aplicarlo al panel: si el backend lo
// rechaza (rango inválido), la promesa falla y el panel no se recalcula. Si es
// válido, la respuesta queda en caché para la sección que la usa.
export function useValidarConsultaPeriodo() {
  const queryClient = useQueryClient()
  return (consulta: ConsultaPeriodo) => queryClient.fetchQuery(opcionesResumenDashboard(consulta))
}
