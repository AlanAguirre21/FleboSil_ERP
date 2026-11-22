import { act, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import type {
  ResumenDashboard, ResumenVentas, ResumenCompras, ProductoTop, ClienteTop, MovimientoCajaReporte, ResumenFacturacion,
  ResumenProduccion,
} from '../../api/reportes'
import { useResumenDashboard, useValidarConsultaPeriodo } from '../../hooks/useResumenDashboard'
import { useResumenProduccion } from '../../hooks/useResumenProduccion'
import { useResumenVentas } from '../../hooks/useResumenVentas'
import { useResumenCompras } from '../../hooks/useResumenCompras'
import { useProductosTop } from '../../hooks/useProductosTop'
import { useClientesTop } from '../../hooks/useClientesTop'
import { useResumenFacturacion } from '../../hooks/useResumenFacturacion'
import { useMovimientosCajaDashboard } from '../../hooks/useMovimientosCajaDashboard'
import { useSaldoCaja } from '../../hooks/useMovimientosCaja'
import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import { Dashboard } from './Dashboard'

const navigateMock = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => navigateMock }
})

vi.mock('../../hooks/useResumenDashboard')
vi.mock('../../hooks/useResumenVentas')
vi.mock('../../hooks/useResumenCompras')
vi.mock('../../hooks/useProductosTop')
vi.mock('../../hooks/useClientesTop')
vi.mock('../../hooks/useResumenFacturacion')
vi.mock('../../hooks/useResumenProduccion')
vi.mock('../../hooks/useMovimientosCajaDashboard')
vi.mock('../../hooks/useMovimientosCaja')
vi.mock('../../hooks/useUsuarioActual')

function resumenBase(overrides: Partial<ResumenDashboard> = {}): ResumenDashboard {
  return {
    periodo: 'dia',
    granularidad: 'hora',
    ventas_total: '500.00',
    compras_total: '200.00',
    ganancia: '300.00',
    periodo_anterior: { inicio: '2026-08-24T00:00:00-06:00', fin: '2026-08-24T10:30:00-06:00' },
    anterior: { ventas_total: '400.00', compras_total: '160.00', ganancia: '200.00' },
    variacion: { ventas_total: '25.0', compras_total: '25.0', ganancia: '50.0' },
    serie: [
      { fecha: '2026-08-25T08:00:00-06:00', ganancia: '100.00' },
      { fecha: '2026-08-25T09:00:00-06:00', ganancia: '200.00' },
    ],
    ...overrides,
  }
}

function resumenVentasBase(overrides: Partial<ResumenVentas> = {}): ResumenVentas {
  return {
    periodo: 'dia',
    granularidad: 'hora',
    numero_ventas: 7,
    ticket_promedio: '71.43',
    periodo_anterior: { inicio: '2026-08-24T00:00:00-06:00', fin: '2026-08-24T10:30:00-06:00' },
    anterior: { numero_ventas: 5, ticket_promedio: '80.00' },
    variacion: { numero_ventas: '40.0', ticket_promedio: '-10.7' },
    con_envio: [{ fecha: '2026-08-25T08:00:00-06:00', monto: '220.00' }],
    sin_envio: [{ fecha: '2026-08-25T08:00:00-06:00', monto: '200.00' }],
    envio: [{ fecha: '2026-08-25T08:00:00-06:00', monto: '20.00' }],
    conteo_estado: [
      { tipo: 'Pendiente', cantidad: 2 },
      { tipo: 'Entregada', cantidad: 5 },
    ],
    ...overrides,
  }
}

function resumenComprasBase(overrides: Partial<ResumenCompras> = {}): ResumenCompras {
  return {
    periodo: 'dia',
    granularidad: 'hora',
    todas: [{ fecha: '2026-08-25T08:00:00-06:00', monto: '300.00' }],
    productos: [{ fecha: '2026-08-25T08:00:00-06:00', monto: '200.00' }],
    insumos: [{ fecha: '2026-08-25T08:00:00-06:00', monto: '100.00' }],
    conteo_estado: [
      { tipo: 'Pendiente', cantidad: 1 },
      { tipo: 'Recibida', cantidad: 3 },
    ],
    ...overrides,
  }
}

const productosBase: ProductoTop[] = [{ producto: 'Medias de compresión', cantidad: '10.00' }]
const clientesBase: ClienteTop[] = [{ cliente: 'María Pérez', monto: '1500.00' }]
const movimientosBase: MovimientoCajaReporte[] = [
  { fecha: '2026-08-25T08:00:00-06:00', tipo_movimiento: 'ingreso', observacion: 'Venta #1' },
]

function resumenFacturacionBase(overrides: Partial<ResumenFacturacion> = {}): ResumenFacturacion {
  return {
    periodo: 'dia',
    granularidad: 'hora',
    periodo_anterior: { inicio: '2026-08-24T00:00:00-06:00', fin: '2026-08-24T10:30:00-06:00' },
    anterior: { facturado_total: '1000.00' },
    variacion: { facturado_total: '50.0' },
    facturado_total: '1500.00',
    facturas_emitidas: 2,
    por_cobrar_ppd: '700.00',
    porcentaje_facturado: '75.0',
    serie: [{ fecha: '2026-10-18T10:00:00-06:00', total: '1500.00', pue: '800.00', ppd: '700.00' }],
    conteo_estado: [
      { estado: 'timbrada', tipo: 'Timbrada', cantidad: 2 },
      { estado: 'pendiente', tipo: 'Pendiente', cantidad: 0 },
      { estado: 'error', tipo: 'Error', cantidad: 1 },
      { estado: 'pendiente_cancelacion', tipo: 'Pendiente de cancelación', cantidad: 0 },
      { estado: 'cancelada', tipo: 'Cancelada', cantidad: 0 },
    ],
    requiere_atencion: [
      { id: 7, serie: 'A', folio_interno: 12, cliente: 'Hospital Santa Rosa', total: '80.00', estado: 'error', fecha: '2026-10-01T10:00:00Z' },
      { id: 9, serie: '', folio_interno: null, cliente: 'Sin cliente', total: '40.00', estado: 'pendiente_cancelacion', fecha: '2026-10-02T10:00:00Z' },
    ],
    ...overrides,
  }
}

function resumenProduccionBase(overrides: Partial<ResumenProduccion> = {}): ResumenProduccion {
  return {
    periodo: 'dia',
    granularidad: 'hora',
    producciones: 3,
    unidades_producidas: '18.00',
    costo_total: '330.00',
    serie: [{ fecha: '2026-08-25T08:00:00-06:00', unidades: '18.00' }],
    top_productos: [{ producto: 'Medias de compresión', cantidad: '15.00' }],
    ...overrides,
  }
}

function mockearTodo({
  usuario = { nombre: 'Ana', rol: 'admin' as const },
  saldo = { saldo_actual: '1000.00', saldo_adicional: '0.00', saldo_total: '1000.00' },
  resumenFacturacion = resumenFacturacionBase(),
  resumenProduccion = resumenProduccionBase(),
  validarConsulta = vi.fn().mockResolvedValue(resumenBase()),
}: {
  usuario?: { nombre: string; rol: 'admin' | 'operador' } | undefined
  saldo?: { saldo_actual: string; saldo_adicional: string; saldo_total: string }
  resumenFacturacion?: ResumenFacturacion
  resumenProduccion?: ResumenProduccion
  validarConsulta?: ReturnType<typeof vi.fn>
} = {}) {
  vi.mocked(useResumenDashboard).mockReturnValue(
    { data: resumenBase(), isLoading: false } as unknown as ReturnType<typeof useResumenDashboard>,
  )
  vi.mocked(useResumenVentas).mockReturnValue(
    { data: resumenVentasBase(), isLoading: false } as unknown as ReturnType<typeof useResumenVentas>,
  )
  vi.mocked(useResumenCompras).mockReturnValue(
    { data: resumenComprasBase(), isLoading: false } as unknown as ReturnType<typeof useResumenCompras>,
  )
  vi.mocked(useProductosTop).mockReturnValue(
    { data: productosBase, isLoading: false } as unknown as ReturnType<typeof useProductosTop>,
  )
  vi.mocked(useClientesTop).mockReturnValue(
    { data: clientesBase, isLoading: false } as unknown as ReturnType<typeof useClientesTop>,
  )
  vi.mocked(useMovimientosCajaDashboard).mockReturnValue(
    { data: movimientosBase, isLoading: false } as unknown as ReturnType<typeof useMovimientosCajaDashboard>,
  )
  vi.mocked(useSaldoCaja).mockReturnValue(
    { data: saldo, isLoading: false } as unknown as ReturnType<typeof useSaldoCaja>,
  )
  vi.mocked(useUsuarioActual).mockReturnValue(
    { data: usuario, isLoading: false } as unknown as ReturnType<typeof useUsuarioActual>,
  )
  vi.mocked(useResumenFacturacion).mockReturnValue(
    { data: resumenFacturacion, isLoading: false } as unknown as ReturnType<typeof useResumenFacturacion>,
  )
  vi.mocked(useResumenProduccion).mockReturnValue(
    { data: resumenProduccion, isLoading: false } as unknown as ReturnType<typeof useResumenProduccion>,
  )
  vi.mocked(useValidarConsultaPeriodo).mockReturnValue(
    validarConsulta as unknown as ReturnType<typeof useValidarConsultaPeriodo>,
  )
  return { validarConsulta }
}

function renderDashboard() {
  return render(
    <MemoryRouter>
      <Dashboard />
    </MemoryRouter>,
  )
}

describe('Dashboard', () => {
  it('muestra el logotipo en el encabezado en lugar del título de texto', () => {
    mockearTodo()
    renderDashboard()

    expect(screen.getByRole('img', { name: 'FleboSil' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Resumen FleboSil' })).not.toBeInTheDocument()
  })

  // 016, "Actualización: periodos ampliados, comparación y producción": de 4 a 5 opciones.
  it('el admin ve las 5 opciones de periodo', () => {
    mockearTodo()
    renderDashboard()

    const nombres = screen.getAllByRole('tab').map((pestaña) => pestaña.textContent)
    expect(nombres).toEqual(['Día', 'Semana', 'Mes', 'Año', 'Personalizado'])
  })

  it('el rol operador solo ve la pestaña "Día", sin Semana/Mes/Año', () => {
    mockearTodo({ usuario: { nombre: 'Luis', rol: 'operador' } })
    renderDashboard()

    expect(screen.getByRole('tab', { name: 'Día' })).toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Semana' })).not.toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Mes' })).not.toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Año' })).not.toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Personalizado' })).not.toBeInTheDocument()
    expect(screen.getAllByRole('tab')).toHaveLength(1)
  })

  it('cambiar de periodo recalcula los datos de las secciones sin recargar', () => {
    mockearTodo()
    renderDashboard()

    fireEvent.click(screen.getByRole('tab', { name: 'Año' }))

    expect(useResumenDashboard).toHaveBeenLastCalledWith({ periodo: 'año' })
    expect(useResumenVentas).toHaveBeenLastCalledWith({ periodo: 'año' })
    expect(useResumenCompras).toHaveBeenLastCalledWith({ periodo: 'año' })
    expect(useResumenProduccion).toHaveBeenLastCalledWith({ periodo: 'año' })

    fireEvent.click(screen.getByRole('tab', { name: 'Semana' }))
    expect(useResumenVentas).toHaveBeenLastCalledWith({ periodo: 'semana' })
  })

  it('muestra "Saldo actual de la caja" para el rol admin', () => {
    mockearTodo({ usuario: { nombre: 'Ana', rol: 'admin' } })
    renderDashboard()

    expect(screen.getByText('Saldo actual de la caja')).toBeInTheDocument()
    expect(screen.getByText('$1,000.00')).toBeInTheDocument()
  })

  it('no muestra "Saldo actual de la caja" para el rol operador', () => {
    mockearTodo({ usuario: { nombre: 'Luis', rol: 'operador' } })
    renderDashboard()

    expect(screen.queryByText('Saldo actual de la caja')).not.toBeInTheDocument()
  })

  it('muestra las 7 secciones del panel', () => {
    mockearTodo()
    renderDashboard()

    expect(screen.getByRole('heading', { name: 'Ganancias del periodo' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Resumen de ventas' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Resumen de compras' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Resumen de producción' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Resumen de productos' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Resumen clientes' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Resumen facturación' })).toBeInTheDocument()
  })

  it('muestra "Ganancia de ventas" y "Gasto en compras" junto a sus botones respectivos', () => {
    mockearTodo()
    renderDashboard()

    expect(screen.getByText('Ganancia de ventas')).toBeInTheDocument()
    expect(screen.getByText('$500.00')).toBeInTheDocument()

    expect(screen.getByText('Gasto en compras')).toBeInTheDocument()
    expect(screen.getByText('$200.00')).toBeInTheDocument()
  })

  it('"Nueva venta" vive en Resumen de ventas y navega al formulario de Ventas', () => {
    mockearTodo()
    renderDashboard()

    fireEvent.click(screen.getByRole('button', { name: 'Nueva venta' }))
    expect(navigateMock).toHaveBeenCalledWith('/ventas/nueva')
  })

  it('"Nueva compra" vive en Resumen de compras y navega al formulario de Compras', () => {
    mockearTodo()
    renderDashboard()

    fireEvent.click(screen.getByRole('button', { name: 'Nueva compra' }))
    expect(navigateMock).toHaveBeenCalledWith('/compras/nueva')
  })

  it('el ranking de productos alterna entre más y menos vendidos', () => {
    mockearTodo()
    renderDashboard()

    fireEvent.click(screen.getByRole('button', { name: 'Menos vendidos' }))
    expect(useProductosTop).toHaveBeenLastCalledWith({ periodo: 'dia' }, 'menos', 'cantidad')
  })

  it('el ranking de clientes alterna entre más y menos compras', () => {
    mockearTodo()
    renderDashboard()

    fireEvent.click(screen.getByRole('button', { name: 'Menos compras' }))
    expect(useClientesTop).toHaveBeenLastCalledWith({ periodo: 'dia' }, 'menos')
  })

  it('el selector de movimientos financieros ofrece 5, 10 y todos', () => {
    mockearTodo()
    renderDashboard()

    fireEvent.click(screen.getByRole('button', { name: 'Todos' }))
    expect(useMovimientosCajaDashboard).toHaveBeenLastCalledWith({ periodo: 'dia' }, 'todos')
  })

  it('la lista de movimientos financieros solo muestra fecha, tipo y descripción, nunca el monto', () => {
    mockearTodo()
    renderDashboard()

    const descripcion = screen.getByText('Venta #1')
    expect(descripcion).toBeInTheDocument()
    expect(screen.getByText('Ingreso')).toBeInTheDocument()

    const fila = descripcion.closest('li')
    expect(fila).not.toBeNull()
    expect(fila).not.toHaveTextContent(/\$\d/)
  })

  // 016, "Actualización: Resumen facturación con datos" — reemplaza el
  // test del placeholder "En construcción".
  it('"Resumen facturación" muestra sus indicadores en lugar del mensaje de construcción', () => {
    mockearTodo()
    renderDashboard()

    expect(screen.queryByText('En construcción')).not.toBeInTheDocument()
    const recuadro = (etiqueta: string) => screen.getByText(etiqueta, { selector: '.statLabel' }).parentElement
    expect(recuadro('Facturado')).toHaveTextContent('$1,500.00')
    expect(recuadro('Facturas emitidas')).toHaveTextContent('2')
    expect(recuadro('Por cobrar (PPD)')).toHaveTextContent('$700.00')
    expect(recuadro('Por cobrar (PPD)')).toHaveClass('statTileWarning')
    expect(recuadro('% de ventas facturadas')).toHaveTextContent('75.0 %')
    expect(useResumenFacturacion).toHaveBeenLastCalledWith({ periodo: 'dia' })
  })

  it('sin ventas el % facturado muestra "—" y sin saldo PPD no se tiñe', () => {
    mockearTodo({ resumenFacturacion: resumenFacturacionBase({ porcentaje_facturado: null, por_cobrar_ppd: '0.00' }) })
    renderDashboard()

    const recuadro = (etiqueta: string) => screen.getByText(etiqueta, { selector: '.statLabel' }).parentElement
    expect(recuadro('% de ventas facturadas')).toHaveTextContent('—')
    expect(recuadro('Por cobrar (PPD)')).not.toHaveClass('statTileWarning')
  })

  it('"Requiere atención" enlaza cada factura a su detalle y a Facturación', () => {
    mockearTodo()
    renderDashboard()

    expect(screen.getByRole('link', { name: 'A-12' })).toHaveAttribute('href', '/facturacion/7')
    expect(screen.getByRole('link', { name: 'Factura #9' })).toHaveAttribute('href', '/facturacion/9')
    expect(screen.getByText('Pendiente de cancelación', { selector: '.status' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Ver todas en Facturación' })).toHaveAttribute('href', '/facturacion')
    expect(screen.getByText(/sin importar el periodo/i)).toBeInTheDocument()
  })

  it('sin facturas por atender muestra el estado vacío', () => {
    mockearTodo({ resumenFacturacion: resumenFacturacionBase({ requiere_atencion: [] }) })
    renderDashboard()

    expect(screen.getByText('No hay facturas que requieran atención.')).toBeInTheDocument()
  })

  it('el operador ve el mismo Resumen facturación', () => {
    mockearTodo({ usuario: { nombre: 'Luis', rol: 'operador' } })
    renderDashboard()

    expect(screen.getByText('Facturado', { selector: '.statLabel' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'A-12' })).toBeInTheDocument()
  })

  it('muestra un estado vacío en Ganancias del periodo cuando no hay datos suficientes', () => {
    mockearTodo()
    vi.mocked(useResumenDashboard).mockReturnValue(
      {
        data: resumenBase({ ventas_total: '0.00', compras_total: '0.00', ganancia: '0.00', serie: [] }),
        isLoading: false,
      } as unknown as ReturnType<typeof useResumenDashboard>,
    )
    renderDashboard()

    expect(screen.getByText(/todavía no hay suficientes datos/i)).toBeInTheDocument()
  })

  // 016, "Actualización: ganancias y movimientos de caja solo para admin".
  it('el operador no ve la sección de ganancias ni los movimientos financieros', () => {
    mockearTodo({ usuario: { nombre: 'Luis', rol: 'operador' } })
    vi.mocked(useMovimientosCajaDashboard).mockClear()
    renderDashboard()

    expect(screen.queryByRole('heading', { name: 'Ganancias del periodo' })).not.toBeInTheDocument()
    expect(screen.queryByText('Movimientos financieros del periodo')).not.toBeInTheDocument()
    expect(screen.queryByText('Ganancia del periodo')).not.toBeInTheDocument()
    // Ni siquiera se pide la lista: el endpoint es solo de admin.
    expect(useMovimientosCajaDashboard).not.toHaveBeenCalled()
    expect(screen.getByRole('heading', { name: 'Resumen de ventas' })).toBeInTheDocument()
    expect(screen.getByText('Ganancia de ventas')).toBeInTheDocument()
  })

  it('el admin sigue viendo la sección de ganancias y los movimientos financieros', () => {
    mockearTodo({ usuario: { nombre: 'Ana', rol: 'admin' } })
    renderDashboard()

    expect(screen.getByRole('heading', { name: 'Ganancias del periodo' })).toBeInTheDocument()
    expect(screen.getByText('Movimientos financieros del periodo')).toBeInTheDocument()
  })

  // 016, "Actualización: cifras propias para el operador".
  it('el operador ve que las cifras son de sus propios registros; el admin no', () => {
    mockearTodo({ usuario: { nombre: 'Luis', rol: 'operador' } })
    const { unmount } = renderDashboard()
    expect(screen.getByText('Cifras de tus propias ventas, compras y facturas.')).toBeInTheDocument()
    unmount()

    mockearTodo({ usuario: { nombre: 'Ana', rol: 'admin' } })
    renderDashboard()
    expect(screen.queryByText('Cifras de tus propias ventas, compras y facturas.')).not.toBeInTheDocument()
  })

  // --- 016, "Actualización: periodos ampliados, comparación y producción" ---

  it('"Personalizado" muestra el rango y solo recalcula al pulsar "Aplicar"', async () => {
    const { validarConsulta } = mockearTodo()
    renderDashboard()

    fireEvent.click(screen.getByRole('tab', { name: 'Personalizado' }))
    expect(screen.getByRole('tab', { name: 'Personalizado' })).toHaveAttribute('aria-selected', 'true')
    fireEvent.change(screen.getByLabelText('Desde'), { target: { value: '2026-03-01' } })
    fireEvent.change(screen.getByLabelText('Hasta'), { target: { value: '2026-03-15' } })
    expect(useResumenVentas).toHaveBeenLastCalledWith({ periodo: 'dia' })

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Aplicar' }))
    })

    const rango = { periodo: 'personalizado', desde: '2026-03-01', hasta: '2026-03-15' }
    expect(validarConsulta).toHaveBeenCalledWith(rango)
    expect(useResumenVentas).toHaveBeenLastCalledWith(rango)
    expect(useResumenProduccion).toHaveBeenLastCalledWith(rango)
    expect(screen.getByText('Del 01/03/2026 al 15/03/2026')).toBeInTheDocument()
  })

  it('un rango rechazado por el backend muestra su mensaje y no recalcula el panel', async () => {
    const error = { response: { status: 400, data: { desde: ['"Desde" no puede ser posterior a "Hasta".'] } } }
    mockearTodo({ validarConsulta: vi.fn().mockRejectedValue(error) })
    renderDashboard()

    fireEvent.click(screen.getByRole('tab', { name: 'Personalizado' }))
    fireEvent.change(screen.getByLabelText('Desde'), { target: { value: '2026-03-20' } })
    fireEvent.change(screen.getByLabelText('Hasta'), { target: { value: '2026-03-15' } })
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Aplicar' }))
    })

    expect(screen.getByRole('alert')).toHaveTextContent('"Desde" no puede ser posterior a "Hasta".')
    expect(useResumenVentas).toHaveBeenLastCalledWith({ periodo: 'dia' })
  })

  it('muestra la variación contra el periodo anterior, con compras en tono neutro', () => {
    mockearTodo()
    renderDashboard()

    const variacion = (etiqueta: string) =>
      screen.getByText(etiqueta).closest('span:not([class*="LabelRow"])')?.parentElement?.querySelector('[data-tono]')

    expect(screen.getByText('Ganancia del periodo').parentElement?.parentElement).toHaveTextContent(
      '▲ 50.0 % vs. periodo anterior',
    )
    const tonos = Array.from(document.querySelectorAll('[data-tono]')).map((nodo) => [nodo.textContent, nodo.getAttribute('data-tono')])
    expect(tonos).toContainEqual(['▲ 25.0 % vs. periodo anterior', 'neutro'])
    expect(tonos).toContainEqual(['▲ 25.0 % vs. periodo anterior', 'sube'])
    expect(tonos).toContainEqual(['▼ 10.7 % vs. periodo anterior', 'baja'])
    expect(variacion('Gasto en compras')).toHaveAttribute('data-tono', 'neutro')
    const facturado = screen.getByText('Facturado', { selector: '.statLabel' }).parentElement
    expect(facturado).toHaveTextContent('▲ 50.0 % vs. periodo anterior')
  })

  it('sin base de comparación muestra "Sin datos del periodo anterior"', () => {
    mockearTodo({
      resumenFacturacion: resumenFacturacionBase({
        anterior: { facturado_total: '0.00' },
        variacion: { facturado_total: null },
      }),
    })
    renderDashboard()

    const facturado = screen.getByText('Facturado', { selector: '.statLabel' }).parentElement
    expect(facturado).toHaveTextContent('Sin datos del periodo anterior')
  })

  it('el operador ve la comparación de sus cifras, nunca la de la ganancia', () => {
    mockearTodo({ usuario: { nombre: 'Luis', rol: 'operador' } })
    vi.mocked(useResumenDashboard).mockReturnValue({
      data: {
        periodo: 'dia',
        ventas_total: '500.00',
        compras_total: '200.00',
        anterior: { ventas_total: '400.00', compras_total: '160.00' },
        variacion: { ventas_total: '25.0', compras_total: '25.0' },
      },
      isLoading: false,
    } as unknown as ReturnType<typeof useResumenDashboard>)
    renderDashboard()

    expect(screen.queryByText('Ganancia del periodo')).not.toBeInTheDocument()
    expect(screen.getAllByText('▲ 25.0 % vs. periodo anterior')).toHaveLength(2)
  })

  it('los íconos de ayuda explican "Ganancia del periodo" y "Ganancia de ventas" y se abren con clic', () => {
    mockearTodo()
    renderDashboard()

    const ayudaGanancia = screen.getByRole('button', { name: 'Qué es la ganancia del periodo' })
    expect(ayudaGanancia).toHaveAttribute('aria-expanded', 'false')
    fireEvent.click(ayudaGanancia)
    expect(ayudaGanancia).toHaveAttribute('aria-expanded', 'true')
    expect(ayudaGanancia).toHaveAccessibleDescription('Ventas menos compras del periodo.')
    fireEvent.keyDown(ayudaGanancia, { key: 'Escape' })
    expect(ayudaGanancia).toHaveAttribute('aria-expanded', 'false')

    const ayudaVentas = screen.getByRole('button', { name: 'Qué es la ganancia de ventas' })
    expect(ayudaVentas).toHaveAccessibleDescription('Total vendido en el periodo, incluido el envío.')
  })

  it('el icono junto al selector explica qué fechas abarca el periodo elegido', async () => {
    mockearTodo()
    renderDashboard()

    const ayudaPeriodo = screen.getByRole('button', { name: 'Qué fechas abarca el periodo' })
    expect(ayudaPeriodo).toHaveAccessibleDescription(/^Hoy \(\d{2}\/\d{2}\/\d{4}\), desde las 00:00 hasta ahora\.$/)

    fireEvent.click(screen.getByRole('tab', { name: 'Mes' }))
    expect(ayudaPeriodo).toHaveAccessibleDescription(/^Del 01\/\d{2}\/\d{4} a hoy\.$/)

    fireEvent.click(screen.getByRole('tab', { name: 'Personalizado' }))
    expect(ayudaPeriodo).toHaveAccessibleDescription('Elige las fechas y pulsa "Aplicar".')
    fireEvent.change(screen.getByLabelText('Desde'), { target: { value: '2026-03-01' } })
    fireEvent.change(screen.getByLabelText('Hasta'), { target: { value: '2026-03-15' } })
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Aplicar' }))
    })
    expect(ayudaPeriodo).toHaveAccessibleDescription('Del 01/03/2026 al 15/03/2026, ambos incluidos.')
  })

  it('el operador también tiene la ayuda del periodo "Día"', () => {
    mockearTodo({ usuario: { nombre: 'Luis', rol: 'operador' } })
    renderDashboard()

    expect(screen.getByRole('button', { name: 'Qué fechas abarca el periodo' })).toHaveAccessibleDescription(/^Hoy /)
  })

  it('Resumen de ventas muestra el número de ventas y el ticket promedio', () => {
    mockearTodo()
    renderDashboard()

    expect(screen.getByText('Número de ventas').parentElement).toHaveTextContent('7')
    expect(screen.getByText('Número de ventas').parentElement).toHaveTextContent('▲ 40.0 % vs. periodo anterior')
    expect(screen.getByText('Ticket promedio').parentElement).toHaveTextContent('$71.43')
  })

  it('sin ventas el ticket promedio muestra "—"', () => {
    mockearTodo()
    vi.mocked(useResumenVentas).mockReturnValue({
      data: resumenVentasBase({
        numero_ventas: 0,
        ticket_promedio: null,
        variacion: { numero_ventas: null, ticket_promedio: null },
      }),
      isLoading: false,
    } as unknown as ReturnType<typeof useResumenVentas>)
    renderDashboard()

    expect(screen.getByText('Ticket promedio').parentElement).toHaveTextContent('—')
    expect(screen.getByText('Ticket promedio').parentElement).toHaveTextContent('Sin datos del periodo anterior')
  })

  it('el admin puede ordenar el top de productos por importe', () => {
    mockearTodo()
    renderDashboard()

    fireEvent.click(screen.getByRole('button', { name: 'Importe' }))
    expect(useProductosTop).toHaveBeenLastCalledWith({ periodo: 'dia' }, 'mas', 'importe')
  })

  it('el operador no ve el control "Unidades / Importe"', () => {
    mockearTodo({ usuario: { nombre: 'Luis', rol: 'operador' } })
    renderDashboard()

    expect(screen.queryByRole('button', { name: 'Importe' })).not.toBeInTheDocument()
    expect(useProductosTop).toHaveBeenLastCalledWith({ periodo: 'dia' }, 'mas', 'cantidad')
  })

  it('Resumen de producción muestra sus indicadores y lleva a Producción', () => {
    mockearTodo()
    renderDashboard()

    expect(screen.getByText('Producciones').parentElement).toHaveTextContent('3')
    expect(screen.getByText('Unidades producidas', { selector: 'span' }).parentElement).toHaveTextContent('18')
    expect(screen.getByText('Costo de producción').parentElement).toHaveTextContent('$330.00')

    fireEvent.click(screen.getByRole('button', { name: 'Ir a Producción' }))
    expect(navigateMock).toHaveBeenCalledWith('/produccion')
  })

  it('el operador ve Resumen de producción sin el costo', () => {
    const { costo_total: _sinCosto, ...sinCosto } = resumenProduccionBase()
    void _sinCosto
    mockearTodo({ usuario: { nombre: 'Luis', rol: 'operador' }, resumenProduccion: sinCosto })
    renderDashboard()

    expect(screen.getByRole('heading', { name: 'Resumen de producción' })).toBeInTheDocument()
    expect(screen.queryByText('Costo de producción')).not.toBeInTheDocument()
  })

  it('cada variación tiene un icono que indica contra qué fechas se compara', () => {
    mockearTodo()
    renderDashboard()

    // Ganancia, Ganancia de ventas, Número de ventas, Ticket promedio, Gasto en compras y Facturado.
    const ayudas = screen.getAllByRole('button', { name: 'Con qué periodo se compara' })
    expect(ayudas).toHaveLength(6)
    const primera = ayudas[0] as HTMLElement
    fireEvent.click(primera)
    expect(primera).toHaveAttribute('aria-expanded', 'true')
    expect(primera).toHaveAccessibleDescription('Comparado con el 24/08/2026, de 00:00 a 10:30.')
  })
})
