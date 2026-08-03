import { useQuery } from '@tanstack/react-query'

import { getUsuarioActual } from '../api/usuarios'

export function useUsuarioActual() {
  return useQuery({
    queryKey: ['usuario-actual'],
    queryFn: getUsuarioActual,
    retry: false,
  })
}
