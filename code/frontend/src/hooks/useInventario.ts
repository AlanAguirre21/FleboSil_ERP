import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { ajustarInventario, crearTraslado, getStock, type TipoItemInventario } from '../api/inventario'

export function useStock(tipo: TipoItemInventario, sucursalId: number | null) {
  return useQuery({
    queryKey: ['stock', tipo, sucursalId],
    queryFn: () => getStock(tipo, sucursalId as number),
    enabled: sucursalId !== null,
  })
}

// Lo que un cambio de existencias deja desactualizado: tabla, historial, las
// alertas de stock y la campana del Header.
function invalidarExistencias(queryClient: ReturnType<typeof useQueryClient>) {
  return Promise.all([
    queryClient.invalidateQueries({ queryKey: ['stock'] }),
    queryClient.invalidateQueries({ queryKey: ['movimientos-inventario'] }),
    queryClient.invalidateQueries({ queryKey: ['alertas-stock'] }),
    queryClient.invalidateQueries({ queryKey: ['notificaciones'] }),
  ])
}

export function useAjustarInventario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ajustarInventario,
    onSuccess: () => invalidarExistencias(queryClient),
  })
}

export function useCrearTraslado() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: crearTraslado,
    onSuccess: () => invalidarExistencias(queryClient),
  })
}
