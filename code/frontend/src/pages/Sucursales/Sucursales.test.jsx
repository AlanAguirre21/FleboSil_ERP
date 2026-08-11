import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import {
  useCrearSucursal,
  useDesactivarSucursal,
  useEditarSucursal,
  useSucursales,
} from '../../hooks/useSucursales'
import { Sucursales } from './Sucursales'

vi.mock('../../hooks/useUsuarioActual')
vi.mock('../../hooks/useSucursales')

const SUCURSALES = [
  { id: 1, nombre_sucursal: 'Matriz', ubicacion_sucursal: 'Centro', telefono_sucursal: '555-0001', activo: true },
  { id: 2, nombre_sucursal: 'Norte', ubicacion_sucursal: 'Av. Norte', telefono_sucursal: '555-0002', activo: false },
]

function mockearHooksSucursales() {
  useSucursales.mockReturnValue({ data: SUCURSALES, isLoading: false })
  useCrearSucursal.mockReturnValue({ mutateAsync: vi.fn(), isPending: false })
  useEditarSucursal.mockReturnValue({ mutateAsync: vi.fn(), isPending: false })
  useDesactivarSucursal.mockReturnValue({ mutateAsync: vi.fn(), isPending: false })
}

describe('Sucursales', () => {
  it('renderiza la tabla con los datos de cada sucursal', () => {
    mockearHooksSucursales()
    useUsuarioActual.mockReturnValue({ data: { rol: 'operador' } })

    render(<Sucursales />)

    expect(screen.getByText('Matriz')).toBeInTheDocument()
    expect(screen.getByText('Centro')).toBeInTheDocument()
    expect(screen.getByText('555-0001')).toBeInTheDocument()
    expect(screen.getByText('Activa')).toBeInTheDocument()
    expect(screen.getByText('Norte')).toBeInTheDocument()
    expect(screen.getByText('Inactiva')).toBeInTheDocument()
  })

  it('rol operador no ve botones de crear, editar ni desactivar', () => {
    mockearHooksSucursales()
    useUsuarioActual.mockReturnValue({ data: { rol: 'operador' } })

    render(<Sucursales />)

    expect(screen.queryByRole('button', { name: /nueva sucursal/i })).not.toBeInTheDocument()
    expect(screen.queryByText('Editar')).not.toBeInTheDocument()
    expect(screen.queryByText('Desactivar')).not.toBeInTheDocument()
  })

  it('rol admin ve botones de crear, editar y desactivar', () => {
    mockearHooksSucursales()
    useUsuarioActual.mockReturnValue({ data: { rol: 'admin' } })

    render(<Sucursales />)

    expect(screen.getByRole('button', { name: /nueva sucursal/i })).toBeInTheDocument()
    expect(screen.getAllByText('Editar')).toHaveLength(2)
    // Solo la sucursal activa (Matriz) muestra el botón de desactivar.
    expect(screen.getAllByText('Desactivar')).toHaveLength(1)
  })
})
