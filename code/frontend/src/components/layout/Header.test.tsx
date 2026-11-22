import { fireEvent, render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { Notificaciones, SeccionNotificacion } from '../../api/notificaciones'
import { useAuth } from '../../context/AuthContext'
import { useNotificaciones } from '../../hooks/useNotificaciones'
import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import { Header } from './Header'

vi.mock('../../hooks/useUsuarioActual')
vi.mock('../../hooks/useNotificaciones')
vi.mock('../../context/AuthContext')

// Los mocks solo necesitan el subconjunto de campos que Header realmente lee;
// completar todo el tipo UseQueryResult en cada test sería ruido sin valor real.
function mockUsuarioActual(data: unknown) {
  vi.mocked(useUsuarioActual).mockReturnValue(data as ReturnType<typeof useUsuarioActual>)
}

function mockNotificaciones(data: Notificaciones | undefined, isLoading = false) {
  vi.mocked(useNotificaciones).mockReturnValue({ data, isLoading } as unknown as ReturnType<typeof useNotificaciones>)
}

const SECCION_STOCK: SeccionNotificacion = {
  clave: 'stock',
  titulo: 'Stock',
  ruta: '/inventario',
  total: 2,
  requieren_accion: 2,
  elementos: [
    { titulo: 'Suero', detalle: 'Matriz · 1 de 5 mínimo', etiqueta: null, urgente: true, ruta: '/inventario' },
    { titulo: 'Cloruro', detalle: 'Norte · 2 de 5 mínimo', etiqueta: null, urgente: true, ruta: '/inventario' },
  ],
}

const SECCION_VENTAS: SeccionNotificacion = {
  clave: 'ventas',
  titulo: 'Ventas por entregar',
  ruta: '/ventas',
  total: 7,
  requieren_accion: 1,
  elementos: [
    {
      titulo: 'Venta #12', detalle: 'Clínica Norte · Entrega 18/11/2026', etiqueta: 'Vencida · hace 4 días',
      urgente: true, ruta: '/ventas/12',
    },
    { titulo: 'Venta #15', detalle: 'Sin cliente · Sin fecha de entrega', etiqueta: null, urgente: false, ruta: '/ventas/15' },
  ],
}

const SECCION_FACTURAS: SeccionNotificacion = {
  clave: 'facturas',
  titulo: 'Facturas por atender',
  ruta: '/facturacion',
  total: 1,
  requieren_accion: 0,
  elementos: [
    { titulo: 'A-18', detalle: 'Hospital Santa Rosa', etiqueta: 'Por cobrar $700.00', urgente: false, ruta: '/facturacion/9' },
  ],
}

const SECCION_NOMINAS: SeccionNotificacion = {
  clave: 'nominas',
  titulo: 'Nóminas',
  ruta: '/rrhh?pestana=nominas',
  total: 1,
  requieren_accion: 1,
  elementos: [
    {
      titulo: 'Laura Gómez', detalle: '01/01/2026 – 15/01/2026 · $4,500.00', etiqueta: null, urgente: true,
      ruta: '/rrhh?pestana=nominas',
    },
  ],
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

const campana = () => screen.getByRole('button', { name: /^Notificaciones/ })

describe('Header', () => {
  beforeEach(() => {
    mockUsuarioActual({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    mockNotificaciones({ contador: 0, secciones: [] })
  })

  it('el logo enlaza al Dashboard', () => {
    renderHeader()

    expect(screen.getByRole('link', { name: /FleboSil/i })).toHaveAttribute('href', '/dashboard')
  })

  // 001, "Actualización: centro de notificaciones…": el contador ya no suma
  // todo lo listado, solo lo que requiere acción (lo calcula el backend).
  it('el contador muestra solo lo que requiere acción', () => {
    mockNotificaciones({ contador: 3, secciones: [SECCION_STOCK, SECCION_VENTAS] })

    renderHeader()

    expect(campana()).toHaveAccessibleName('Notificaciones: 3 requieren acción')
    expect(within(campana()).getByText('3')).toBeInTheDocument()
  })

  it('por encima de 9 el contador muestra "9+"', () => {
    mockNotificaciones({ contador: 14, secciones: [SECCION_STOCK] })

    renderHeader()

    expect(within(campana()).getByText('9+')).toBeInTheDocument()
  })

  it('sin nada que requiera acción no muestra contador', () => {
    mockNotificaciones({ contador: 0, secciones: [SECCION_FACTURAS] })

    renderHeader()

    expect(campana()).toHaveAccessibleName('Notificaciones')
    expect(within(campana()).queryByText('0')).not.toBeInTheDocument()
  })

  it('el desplegable agrupa por sección, con su cantidad y "Ver todas"', () => {
    mockNotificaciones({ contador: 3, secciones: [SECCION_STOCK, SECCION_VENTAS, SECCION_FACTURAS] })

    renderHeader()
    fireEvent.click(campana())

    const ventas = screen.getByRole('region', { name: 'Ventas por entregar' })
    expect(within(ventas).getByText('7')).toBeInTheDocument()
    const vencida = within(ventas).getByRole('link', { name: /Venta #12/ })
    expect(vencida).toHaveAttribute('href', '/ventas/12')
    expect(vencida).toHaveTextContent('Vencida · hace 4 días')
    expect(within(ventas).getByRole('link', { name: 'Ver todas: Ventas por entregar' })).toHaveAttribute('href', '/ventas')

    const stock = screen.getByRole('region', { name: 'Stock' })
    expect(within(stock).getByText('Suero')).toBeInTheDocument()
    expect(within(stock).getByText('Matriz · 1 de 5 mínimo')).toBeInTheDocument()

    const facturas = screen.getByRole('region', { name: 'Facturas por atender' })
    expect(within(facturas).getByRole('link', { name: /A-18/ })).toHaveTextContent('Por cobrar $700.00')
  })

  it('las nóminas pendientes enlazan a la pestaña Nóminas de RRHH', () => {
    mockNotificaciones({ contador: 1, secciones: [SECCION_NOMINAS] })

    renderHeader()
    fireEvent.click(campana())

    const solicitud = screen.getByRole('link', { name: /laura gómez/i })
    expect(solicitud).toHaveAttribute('href', '/rrhh?pestana=nominas')
    expect(solicitud).toHaveTextContent('01/01/2026 – 15/01/2026 · $4,500.00')
    expect(screen.queryByRole('button', { name: 'Aprobar' })).not.toBeInTheDocument()
  })

  it('sin pendientes muestra "Todo al día"', () => {
    renderHeader()
    fireEvent.click(campana())

    expect(screen.getByText('Todo al día')).toBeInTheDocument()
  })

  it('muestra estado de carga en vez de afirmar que todo está al día', () => {
    mockNotificaciones(undefined, true)

    renderHeader()
    fireEvent.click(campana())

    expect(screen.getByText(/cargando notificaciones/i)).toBeInTheDocument()
    expect(screen.queryByText('Todo al día')).not.toBeInTheDocument()
  })

  it('cerrar sesión invalida la sesión activa', () => {
    const { logoutMock } = renderHeader()
    fireEvent.click(screen.getByRole('button', { name: /ana/i }))
    fireEvent.click(screen.getByRole('button', { name: /cerrar sesión/i }))

    expect(logoutMock).toHaveBeenCalled()
  })

  it('el avatar del menú de usuario muestra la fotografía si la tiene', () => {
    mockUsuarioActual({
      data: { nombre: 'Ana', rol: 'admin', modulos: [], foto_usuario: 'http://servidor/fotos-usuarios/a.png' },
    })

    renderHeader()

    expect(document.querySelector('img[src="http://servidor/fotos-usuarios/a.png"]')).toBeInTheDocument()
  })

  it('sin fotografía, el avatar del menú de usuario muestra las iniciales', () => {
    mockUsuarioActual({ data: { nombre: 'Ana Torres', rol: 'admin', modulos: [], foto_usuario: null } })

    renderHeader()

    expect(screen.getByText('AT')).toBeInTheDocument()
  })
})

describe('Header — cierre de los menús desplegables', () => {
  beforeEach(() => {
    mockUsuarioActual({ data: { nombre: 'Ana', rol: 'admin', modulos: [] } })
    mockNotificaciones({ contador: 1, secciones: [SECCION_STOCK, SECCION_NOMINAS] })
  })

  const botonUsuario = () => screen.getByRole('button', { name: /ana/i })

  it('un clic fuera cierra el desplegable abierto', () => {
    renderHeader()
    fireEvent.click(campana())
    expect(screen.getByRole('menu')).toBeInTheDocument()

    fireEvent.pointerDown(document.body)

    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
    expect(campana()).toHaveAttribute('aria-expanded', 'false')
  })

  it('un clic dentro del desplegable no lo cierra', () => {
    renderHeader()
    fireEvent.click(campana())

    fireEvent.pointerDown(screen.getByText('Stock', { selector: 'span' }))

    expect(screen.getByRole('menu')).toBeInTheDocument()
  })

  it('Escape cierra el desplegable y devuelve el foco a su botón', () => {
    renderHeader()
    fireEvent.click(botonUsuario())
    expect(screen.getByRole('menu')).toBeInTheDocument()

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
    expect(botonUsuario()).toHaveFocus()
  })

  it('se cierra cuando el foco del teclado sale del desplegable', () => {
    renderHeader()
    fireEvent.click(botonUsuario())

    fireEvent.focusOut(screen.getByRole('button', { name: /cerrar sesión/i }), { relatedTarget: campana() })

    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })

  it('solo un desplegable abierto a la vez', () => {
    renderHeader()
    fireEvent.click(campana())
    fireEvent.click(botonUsuario())

    expect(screen.getAllByRole('menu')).toHaveLength(1)
    expect(campana()).toHaveAttribute('aria-expanded', 'false')
    expect(botonUsuario()).toHaveAttribute('aria-expanded', 'true')
  })

  it('al navegar desde el menú de usuario, el menú se cierra', () => {
    renderHeader()
    fireEvent.click(botonUsuario())

    fireEvent.click(screen.getByRole('link', { name: /información de usuario/i }))

    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })

  it('seguir el enlace de una notificación cierra el desplegable', () => {
    renderHeader()
    fireEvent.click(campana())

    fireEvent.click(screen.getByRole('link', { name: /laura gómez/i }))

    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })

  it('con todo cerrado, un clic fuera o Escape no cambian nada', () => {
    renderHeader()

    fireEvent.pointerDown(document.body)
    fireEvent.keyDown(document, { key: 'Escape' })

    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
    fireEvent.click(campana())
    expect(screen.getByRole('menu')).toBeInTheDocument()
  })
})
