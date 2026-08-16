import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { useAuth } from '../../context/AuthContext'
import { useAlertasStock } from '../../hooks/useAlertasStock'
import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import { Header } from './Header'

vi.mock('../../hooks/useUsuarioActual')
vi.mock('../../hooks/useAlertasStock')
vi.mock('../../context/AuthContext')

// Los mocks solo necesitan el subconjunto de campos que Header realmente lee;
// completar todo el tipo UseQueryResult en cada test sería ruido sin valor real.
function mockUsuarioActual(data: unknown) {
  vi.mocked(useUsuarioActual).mockReturnValue(data as ReturnType<typeof useUsuarioActual>)
}

function mockAlertasStock(data: unknown) {
  vi.mocked(useAlertasStock).mockReturnValue(data as ReturnType<typeof useAlertasStock>)
}

function renderHeader() {
  const logoutMock = vi.fn()
  vi.mocked(useAuth).mockReturnValue({
    autenticado: true,
    login: vi.fn(),
    logout: logoutMock,
    iniciarSesionConTokens: vi.fn(),
  })
  render(
    <MemoryRouter>
      <Header onToggleSidebar={() => {}} />
    </MemoryRouter>,
  )
  return { logoutMock }
}

describe('Header', () => {
  it('el logo enlaza al Dashboard', () => {
    mockUsuarioActual({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    mockAlertasStock({ data: [] })

    renderHeader()

    expect(screen.getByRole('link', { name: /FleboSil/i })).toHaveAttribute('href', '/dashboard')
  })

  it('muestra el contador de notificaciones cuando hay alertas de stock', () => {
    mockUsuarioActual({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    mockAlertasStock({
      data: [
        { tipo: 'producto', nombre: 'Suero', sucursal: 'Matriz', stock_actual: 1, stock_minimo: 5 },
        { tipo: 'materia_prima', nombre: 'Cloruro', sucursal: 'Matriz', stock_actual: 1, stock_minimo: 5 },
      ],
    })

    renderHeader()

    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('no muestra contador cuando no hay alertas', () => {
    mockUsuarioActual({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    mockAlertasStock({ data: [] })

    renderHeader()

    expect(screen.queryByText('0')).not.toBeInTheDocument()
  })

  it('el dropdown lista nombre y sucursal de cada ítem en alerta', () => {
    mockUsuarioActual({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    mockAlertasStock({
      data: [
        { tipo: 'producto', nombre: 'Suero', sucursal: 'Matriz', stock_actual: 1, stock_minimo: 5 },
        { tipo: 'materia_prima', nombre: 'Cloruro', sucursal: 'Norte', stock_actual: 1, stock_minimo: 5 },
      ],
    })

    renderHeader()
    fireEvent.click(screen.getByRole('button', { name: /alertas de stock/i }))

    expect(screen.getByText('Suero')).toBeInTheDocument()
    expect(screen.getByText('Matriz')).toBeInTheDocument()
    expect(screen.getByText('Cloruro')).toBeInTheDocument()
    expect(screen.getByText('Norte')).toBeInTheDocument()
  })

  it('muestra estado de carga en vez de afirmar que no hay alertas', () => {
    mockUsuarioActual({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    mockAlertasStock({ data: undefined, isLoading: true })

    renderHeader()
    fireEvent.click(screen.getByRole('button', { name: /alertas de stock/i }))

    expect(screen.getByText(/cargando alertas/i)).toBeInTheDocument()
    expect(screen.queryByText(/sin alertas de stock/i)).not.toBeInTheDocument()
  })

  it('cerrar sesión invalida la sesión activa', () => {
    mockUsuarioActual({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    mockAlertasStock({ data: [] })

    const { logoutMock } = renderHeader()
    fireEvent.click(screen.getByRole('button', { name: /ana/i }))
    fireEvent.click(screen.getByRole('button', { name: /cerrar sesión/i }))

    expect(logoutMock).toHaveBeenCalled()
  })
})
