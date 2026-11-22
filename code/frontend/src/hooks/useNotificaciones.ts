import { useQuery } from '@tanstack/react-query'

import { getNotificaciones } from '../api/notificaciones'

// Campana del Header: se vuelve a pedir cada 60 s y al volver a la pestaña,
// para que una venta o compra nueva aparezca sin recargar la página.
export function useNotificaciones() {
  return useQuery({
    queryKey: ['notificaciones'],
    queryFn: getNotificaciones,
    staleTime: 30_000,
    refetchInterval: 60_000,
    refetchOnWindowFocus: true,
    retry: false,
  })
}
