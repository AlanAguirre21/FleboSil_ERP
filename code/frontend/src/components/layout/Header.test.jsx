import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { useAlertasStock } from '../../hooks/useAlertasStock'
import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import { Header } from './Header'

vi.mock('../../hooks/useUsuarioActual')
vi.mock('../../hooks/useAlertasStock')

function renderHeader() {
  return render(
    <MemoryRouter>
      <Header onToggleSidebar={() => {}} />
    </MemoryRouter>,
  )
}

describe('Header', () => {
  it('el logo enlaza al Dashboard', () => {
    useUsuarioActual.mockReturnValue({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    useAlertasStock.mockReturnValue({ data: [] })

    renderHeader()

    expect(screen.getByRole('link', { name: /FleboSil/i })).toHaveAttribute('href', '/dashboard')
  })

  it('muestra el contador de notificaciones cuando hay alertas de stock', () => {
    useUsuarioActual.mockReturnValue({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    useAlertasStock.mockReturnValue({
      data: [
        { tipo: 'producto', nombre: 'Suero', sucursal: 'Matriz', stock_actual: 1, stock_minimo: 5 },
        { tipo: 'materia_prima', nombre: 'Cloruro', sucursal: 'Matriz', stock_actual: 1, stock_minimo: 5 },
      ],
    })

    renderHeader()

    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('no muestra contador cuando no hay alertas', () => {
    useUsuarioActual.mockReturnValue({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    useAlertasStock.mockReturnValue({ data: [] })

    renderHeader()

    expect(screen.queryByText('0')).not.toBeInTheDocument()
  })

  it('el dropdown lista nombre y sucursal de cada ítem en alerta', () => {
    useUsuarioActual.mockReturnValue({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    useAlertasStock.mockReturnValue({
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
    useUsuarioActual.mockReturnValue({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    useAlertasStock.mockReturnValue({ data: undefined, isLoading: true })

    renderHeader()
    fireEvent.click(screen.getByRole('button', { name: /alertas de stock/i }))

    expect(screen.getByText(/cargando alertas/i)).toBeInTheDocument()
    expect(screen.queryByText(/sin alertas de stock/i)).not.toBeInTheDocument()
  })
})
