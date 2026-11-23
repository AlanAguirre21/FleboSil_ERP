import { act, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { useAjustarInventario, useCrearTraslado, useStock } from '../../hooks/useInventario'
import { useMateriaPrima } from '../../hooks/useMateriaPrima'
import { useMovimientosInventario } from '../../hooks/useMovimientosInventario'
import { useProductos } from '../../hooks/useProductos'
import { useSucursales } from '../../hooks/useSucursales'
import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import { Inventario } from './Inventario'

vi.mock('../../hooks/useSucursales')
vi.mock('../../hooks/useInventario')
vi.mock('../../hooks/useMovimientosInventario')
vi.mock('../../hooks/useProductos')
vi.mock('../../hooks/useMateriaPrima')
vi.mock('../../hooks/useUsuarioActual')

const useSucursalesMock = vi.mocked(useSucursales)
const useStockMock = vi.mocked(useStock)
const useMovimientosInventarioMock = vi.mocked(useMovimientosInventario)
const useAjustarInventarioMock = vi.mocked(useAjustarInventario)

const SUCURSALES = [
  { id: 1, nombre_sucursal: 'Matriz', ubicacion_sucursal: '', telefono_sucursal: '', activo: true },
  { id: 2, nombre_sucursal: 'Norte', ubicacion_sucursal: '', telefono_sucursal: '', activo: true },
]

const STOCK_PRODUCTOS = [
  { id: 1, nombre: 'Suero fisiológico', stock_actual: '2.00', stock_minimo: '10.00', stock_bajo: true },
  { id: 2, nombre: 'Gasa estéril', stock_actual: '50.00', stock_minimo: '10.00', stock_bajo: false },
]

const STOCK_MATERIA_PRIMA = [
  { id: 1, nombre: 'Cloruro de sodio', stock_actual: '1.00', stock_minimo: '5.00', stock_bajo: true },
]

const MOVIMIENTOS = [
  {
    id: 1, fecha: '2026-08-20T10:00:00Z', sucursal: 1, sucursal_nombre: 'Matriz', tipo_item: 'producto' as const,
    item_id: 1, item_nombre: 'Suero fisiológico', tipo_movimiento: 'entrada' as const, cantidad: '20.00',
    motivo: 'compra' as const, referencia_id: null, stock_resultante: '20.00', usuario: 1,
    usuario_nombre: 'admin1', sucursal_contraparte: null, observacion: '',
  },
  {
    id: 2, fecha: '2026-08-21T10:00:00Z', sucursal: 1, sucursal_nombre: 'Matriz', tipo_item: 'producto' as const,
    item_id: 1, item_nombre: 'Suero fisiológico', tipo_movimiento: 'salida' as const, cantidad: '5.00',
    motivo: 'traslado_salida' as const, referencia_id: 12, stock_resultante: '15.00', usuario: 1,
    usuario_nombre: 'admin1', sucursal_contraparte: 'Norte', observacion: '',
  },
  {
    id: 3, fecha: '2026-08-21T10:00:00Z', sucursal: 2, sucursal_nombre: 'Norte', tipo_item: 'producto' as const,
    item_id: 1, item_nombre: 'Suero fisiológico', tipo_movimiento: 'entrada' as const, cantidad: '5.00',
    motivo: 'traslado_entrada' as const, referencia_id: 12, stock_resultante: '5.00', usuario: 1,
    usuario_nombre: 'admin1', sucursal_contraparte: 'Matriz', observacion: '',
  },
]

function mockearHooks(rol: 'admin' | 'operador' = 'operador') {
  useSucursalesMock.mockReturnValue({ data: SUCURSALES, isLoading: false } as unknown as ReturnType<typeof useSucursales>)
  useStockMock.mockImplementation(
    (tipo) =>
      ({
        data: tipo === 'producto' ? STOCK_PRODUCTOS : STOCK_MATERIA_PRIMA,
        isLoading: false,
      }) as unknown as ReturnType<typeof useStock>,
  )
  useMovimientosInventarioMock.mockReturnValue(
    { data: MOVIMIENTOS, isLoading: false } as unknown as ReturnType<typeof useMovimientosInventario>,
  )
  vi.mocked(useProductos).mockReturnValue(
    { data: [{ id: 1, nombre_producto: 'Suero fisiológico' }], isLoading: false } as unknown as ReturnType<typeof useProductos>,
  )
  vi.mocked(useMateriaPrima).mockReturnValue(
    { data: [{ id: 1, nombre_item: 'Cloruro de sodio' }], isLoading: false } as unknown as ReturnType<typeof useMateriaPrima>,
  )
  vi.mocked(useUsuarioActual).mockReturnValue(
    { data: { rol } } as unknown as ReturnType<typeof useUsuarioActual>,
  )
  const ajustar = vi.fn().mockResolvedValue(undefined)
  useAjustarInventarioMock.mockReturnValue(
    { mutateAsync: ajustar, isPending: false } as unknown as ReturnType<typeof useAjustarInventario>,
  )
  vi.mocked(useCrearTraslado).mockReturnValue(
    { mutateAsync: vi.fn(), isPending: false } as unknown as ReturnType<typeof useCrearTraslado>,
  )
  return { ajustar }
}

function primero<T>(elementos: T[]): T {
  const elemento = elementos[0]
  if (!elemento) throw new Error('Se esperaba al menos un elemento.')
  return elemento
}

// Recuadro completo de un indicador (etiqueta + cifra) a partir de su etiqueta.
function indicador(etiqueta: string): HTMLElement {
  const recuadro = screen.getByText(etiqueta, { selector: '.statLabel' }).parentElement
  if (!recuadro) throw new Error(`Indicador "${etiqueta}" sin contenedor`)
  return recuadro
}

describe('Inventario', () => {
  it('muestra el inventario de productos por defecto', () => {
    mockearHooks()
    render(<Inventario />)

    const tablaStock = within(primero(screen.getAllByRole('table')))
    expect(tablaStock.getByText('Suero fisiológico')).toBeInTheDocument()
    expect(tablaStock.getByText('Gasa estéril')).toBeInTheDocument()
    expect(tablaStock.queryByText('Cloruro de sodio')).not.toBeInTheDocument()
  })

  it('cambia a inventario de materia prima sin recargar la página', () => {
    mockearHooks()
    render(<Inventario />)

    fireEvent.click(screen.getByRole('tab', { name: 'Materia prima' }))

    expect(useStockMock).toHaveBeenLastCalledWith('materia_prima', expect.any(Number))
  })

  it('marca visualmente los ítems bajo el stock mínimo', () => {
    mockearHooks()
    render(<Inventario />)

    const tablaStock = within(primero(screen.getAllByRole('table')))
    const filaSuero = tablaStock.getByText('Suero fisiológico').closest('tr')
    const filaGasa = tablaStock.getByText('Gasa estéril').closest('tr')

    expect(filaSuero).toHaveTextContent('Bajo mínimo')
    expect(filaGasa).toHaveTextContent('En existencia')
  })

  it('permite filtrar el stock por sucursal', () => {
    mockearHooks()
    render(<Inventario />)

    const selectSucursal = primero(screen.getAllByLabelText('Sucursal'))
    fireEvent.change(selectSucursal, { target: { value: '2' } })

    expect(useStockMock).toHaveBeenLastCalledWith('producto', 2)
  })

  it('el historial no tiene botones de acción', () => {
    mockearHooks()
    render(<Inventario />)

    fireEvent.click(screen.getByRole('tab', { name: 'Movimientos' }))

    expect(screen.queryByRole('button', { name: /nuevo|crear|editar|eliminar/i })).not.toBeInTheDocument()
  })

  // 011, "Actualización — ajuste de inventario…": reemplaza la edición del
  // mínimo directamente en la fila.
  it('un admin ve la acción "Ajustar" en cada fila; el mínimo ya no se edita en la fila', () => {
    mockearHooks('admin')
    render(<Inventario />)

    expect(screen.getByRole('button', { name: 'Ajustar Suero fisiológico' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ajustar Gasa estéril' })).toBeInTheDocument()
    expect(screen.queryByLabelText(/Stock mínimo de/)).not.toBeInTheDocument()
  })

  it('un operador también ve la acción "Ajustar" y abre el modal', () => {
    mockearHooks('operador')
    render(<Inventario />)

    fireEvent.click(screen.getByRole('button', { name: 'Ajustar Suero fisiológico' }))
    expect(screen.getByRole('dialog', { name: 'Ajustar inventario' })).toBeInTheDocument()
  })

  it.each(['admin', 'operador'] as const)('un %s abre el traslado desde la barra de filtros', (rol) => {
    mockearHooks(rol)
    render(<Inventario />)

    expect(screen.getByText('¿Necesitas mover stock entre sucursales?')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Traslado' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Hacer un traslado' }))

    expect(screen.getByRole('dialog', { name: 'Traslado entre sucursales' })).toBeInTheDocument()
  })

  it('precarga el modal con la sucursal y el tipo seleccionados en la tabla', () => {
    mockearHooks()
    render(<Inventario />)

    fireEvent.click(screen.getByRole('tab', { name: 'Materia prima' }))
    fireEvent.change(primero(screen.getAllByLabelText('Sucursal')), { target: { value: '2' } })
    fireEvent.click(screen.getByRole('button', { name: 'Hacer un traslado' }))

    expect(screen.getByLabelText('Sucursal origen')).toHaveValue('2')
    expect(screen.getByLabelText('Tipo de la línea 1')).toHaveValue('materia_prima')
  })

  it('el historial muestra las filas de traslado con número y sucursal contraparte', () => {
    mockearHooks()
    render(<Inventario />)

    fireEvent.click(screen.getByRole('tab', { name: 'Movimientos' }))

    const historial = within(screen.getByRole('table'))
    expect(historial.getByText('Traslado #12 (salida) → Norte')).toBeInTheDocument()
    expect(historial.getByText('Traslado #12 (entrada) ← Matriz')).toBeInTheDocument()
    expect(historial.getByText('Compra')).toBeInTheDocument()
  })

  it('al operador se le aclara que el historial muestra solo sus movimientos; al admin no', () => {
    mockearHooks('operador')
    const { unmount } = render(<Inventario />)
    fireEvent.click(screen.getByRole('tab', { name: 'Movimientos' }))
    expect(screen.getByText('Solo ves los movimientos que tú registraste.')).toBeInTheDocument()
    unmount()

    mockearHooks('admin')
    render(<Inventario />)
    fireEvent.click(screen.getByRole('tab', { name: 'Movimientos' }))
    expect(screen.queryByText('Solo ves los movimientos que tú registraste.')).not.toBeInTheDocument()
  })

  it('permite filtrar el historial por motivo "Traslado"', () => {
    mockearHooks()
    render(<Inventario />)

    fireEvent.click(screen.getByRole('tab', { name: 'Movimientos' }))
    fireEvent.change(screen.getByLabelText('Motivo'), { target: { value: 'traslado' } })

    expect(useMovimientosInventarioMock).toHaveBeenLastCalledWith(expect.objectContaining({ motivo: 'traslado' }))
  })

  it('muestra los indicadores de existencias y tiñe solo las alertas con valor', () => {
    mockearHooks()
    render(<Inventario />)

    expect(indicador('Ítems')).toHaveTextContent('2')
    expect(indicador('En existencia')).toHaveTextContent('1')
    expect(indicador('Bajo mínimo')).toHaveTextContent('1')
    expect(indicador('Bajo mínimo')).toHaveClass('statTileWarning')
    expect(indicador('Agotados')).toHaveTextContent('0')
    expect(indicador('Agotados')).not.toHaveClass('statTileDanger')
  })

  it('marca como "Agotado" un ítem sin existencia aunque su mínimo sea 0', () => {
    mockearHooks()
    useStockMock.mockReturnValue({
      data: [{ id: 3, nombre: 'Vendas', stock_actual: '0.00', stock_minimo: '0.00', stock_bajo: false }],
      isLoading: false,
    } as unknown as ReturnType<typeof useStock>)
    render(<Inventario />)

    const tablaStock = within(screen.getByRole('table'))
    expect(tablaStock.getByText('Vendas').closest('tr')).toHaveTextContent('Agotado')
    expect(indicador('Agotados')).toHaveTextContent('1')
    expect(indicador('Agotados')).toHaveClass('statTileDanger')
  })

  it('el historial muestra cantidades con signo, existencia resultante e indicadores', () => {
    mockearHooks()
    render(<Inventario />)
    fireEvent.click(screen.getByRole('tab', { name: 'Movimientos' }))

    const historial = within(screen.getByRole('table'))
    const filaCompra = historial.getByText('Compra').closest('tr')
    expect(filaCompra).toHaveTextContent('+20.00')
    expect(filaCompra).toHaveTextContent('Entrada')

    const filaSalida = historial.getByText('Traslado #12 (salida) → Norte').closest('tr')
    // Signo menos tipográfico (U+2212) y saldo después del movimiento.
    expect(filaSalida).toHaveTextContent('\u22125.00')
    expect(filaSalida).toHaveTextContent('15.00')

    expect(indicador('Movimientos')).toHaveTextContent('3')
    expect(indicador('Entradas')).toHaveTextContent('2')
    expect(indicador('Salidas')).toHaveTextContent('1')
  })

  it('pagina el historial de 10 en 10, con selector 10 / 25 / 50 / 100 / Todas', () => {
    mockearHooks()
    const muchos = Array.from({ length: 30 }, (_, i) => ({ ...MOVIMIENTOS[0], id: 100 + i }))
    useMovimientosInventarioMock.mockReturnValue(
      { data: muchos, isLoading: false } as unknown as ReturnType<typeof useMovimientosInventario>,
    )
    render(<Inventario />)
    fireEvent.click(screen.getByRole('tab', { name: 'Movimientos' }))

    const filas = () => within(screen.getByRole('table')).getAllByRole('row').length - 1
    expect(filas()).toBe(10)
    expect(screen.getByText('Mostrando 1–10 de 30')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Página 3' })).toBeInTheDocument()

    fireEvent.change(screen.getByLabelText('Filas por página'), { target: { value: '25' } })
    expect(filas()).toBe(25)
    fireEvent.click(screen.getByRole('button', { name: 'Página 2' }))
    expect(filas()).toBe(5)
    expect(screen.getByText('Mostrando 26–30 de 30')).toBeInTheDocument()

    fireEvent.change(screen.getByLabelText('Filas por página'), { target: { value: 'todas' } })
    expect(filas()).toBe(30)
  })

  it('"Limpiar filtros" solo aparece con algún filtro aplicado y los restablece', () => {
    mockearHooks()
    render(<Inventario />)
    fireEvent.click(screen.getByRole('tab', { name: 'Movimientos' }))
    expect(screen.queryByRole('button', { name: 'Limpiar filtros' })).not.toBeInTheDocument()

    const motivo = screen.getByLabelText('Motivo')
    fireEvent.change(motivo, { target: { value: 'traslado' } })
    fireEvent.click(screen.getByRole('button', { name: 'Limpiar filtros' }))

    expect(motivo).toHaveValue('')
    expect(screen.queryByRole('button', { name: 'Limpiar filtros' })).not.toBeInTheDocument()
  })
})

describe('Inventario — sucursal inicial desde la URL', () => {
  afterEach(() => {
    window.history.replaceState(null, '', '/')
  })

  function abrirCon(busqueda: string) {
    window.history.replaceState(null, '', `/inventario${busqueda}`)
    render(<Inventario />)
  }

  it('usa la sucursal de ?sucursal=ID si está activa', () => {
    mockearHooks()
    abrirCon('?sucursal=2')

    expect(useStockMock).toHaveBeenLastCalledWith('producto', 2)
    expect(primero(screen.getAllByLabelText('Sucursal'))).toHaveValue('2')
  })

  it('ignora el parámetro si la sucursal está inactiva', () => {
    mockearHooks()
    useSucursalesMock.mockReturnValue({
      data: [...SUCURSALES, { id: 3, nombre_sucursal: 'Cerrada', ubicacion_sucursal: '', telefono_sucursal: '', activo: false }],
      isLoading: false,
    } as unknown as ReturnType<typeof useSucursales>)
    abrirCon('?sucursal=3')

    expect(useStockMock).toHaveBeenLastCalledWith('producto', 1)
  })

  it('ignora un id inexistente', () => {
    mockearHooks()
    abrirCon('?sucursal=99')
    expect(useStockMock).toHaveBeenLastCalledWith('producto', 1)
  })

  it('ignora un valor no numérico', () => {
    mockearHooks()
    abrirCon('?sucursal=abc')
    expect(useStockMock).toHaveBeenLastCalledWith('producto', 1)
  })
})

describe('Inventario — ajuste de inventario', () => {
  function abrirAjuste(nombre = 'Suero fisiológico') {
    fireEvent.click(screen.getByRole('button', { name: `Ajustar ${nombre}` }))
    return within(screen.getByRole('dialog', { name: 'Ajustar inventario' }))
  }

  it('cambiar el stock muestra la diferencia, pide motivo y confirma con antes → después', async () => {
    const { ajustar } = mockearHooks('admin')
    render(<Inventario />)
    const modal = abrirAjuste()

    expect(modal.getByText('Suero fisiológico').closest('p')).toHaveTextContent('Suero fisiológico · Matriz')
    fireEvent.change(modal.getByLabelText('Stock actual'), { target: { value: '1.50' } })
    expect(modal.getByText(/−0\.50 \(salida\) sobre 2\.00/)).toBeInTheDocument()

    fireEvent.click(modal.getByRole('button', { name: 'Guardar' }))
    expect(modal.getByRole('alert')).toHaveTextContent('Elige el motivo del ajuste.')

    fireEvent.change(modal.getByLabelText('Motivo del ajuste'), { target: { value: 'merma' } })
    fireEvent.change(modal.getByLabelText('Nota (opcional)'), { target: { value: 'Frasco roto' } })
    fireEvent.click(modal.getByRole('button', { name: 'Guardar' }))

    const confirmacion = within(screen.getByRole('dialog', { name: '¿Estás seguro?' }))
    expect(confirmacion.getByText(/Stock actual:/)).toHaveTextContent('Stock actual: 2.00 → 1.50 (−0.50, Merma o daño: Frasco roto)')
    expect(confirmacion.queryByText(/Stock mínimo:/)).not.toBeInTheDocument()

    await act(async () => {
      fireEvent.click(confirmacion.getByRole('button', { name: 'Confirmar' }))
    })
    expect(ajustar).toHaveBeenCalledWith({
      tipo: 'producto', sucursal: 1, item_id: 1,
      stock_actual: '1.50', stock_actual_visto: '2.00', motivo_ajuste: 'merma', nota: 'Frasco roto',
    })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('cambiar solo el mínimo no pide motivo ni genera ajuste de stock', async () => {
    const { ajustar } = mockearHooks('admin')
    render(<Inventario />)
    const modal = abrirAjuste()

    expect(modal.getByRole('button', { name: 'Guardar' })).toBeDisabled()
    fireEvent.change(modal.getByLabelText('Stock mínimo'), { target: { value: '12' } })
    expect(modal.queryByLabelText('Motivo del ajuste')).not.toBeInTheDocument()
    fireEvent.click(modal.getByRole('button', { name: 'Guardar' }))

    const confirmacion = within(screen.getByRole('dialog', { name: '¿Estás seguro?' }))
    expect(confirmacion.getByText(/Stock mínimo:/)).toHaveTextContent('Stock mínimo: 10 → 12')
    await act(async () => {
      fireEvent.click(confirmacion.getByRole('button', { name: 'Confirmar' }))
    })
    expect(ajustar).toHaveBeenCalledWith({ tipo: 'producto', sucursal: 1, item_id: 1, stock_minimo: '12' })
  })

  it('"Otro" exige una nota', () => {
    mockearHooks('admin')
    render(<Inventario />)
    const modal = abrirAjuste()

    fireEvent.change(modal.getByLabelText('Stock actual'), { target: { value: '5' } })
    fireEvent.change(modal.getByLabelText('Motivo del ajuste'), { target: { value: 'otro' } })
    fireEvent.click(modal.getByRole('button', { name: 'Guardar' }))

    expect(modal.getByRole('alert')).toHaveTextContent('Describe el motivo del ajuste.')
    expect(modal.getByLabelText('Nota')).toBeInTheDocument()
  })

  it('"Volver" regresa al formulario sin perder lo capturado', () => {
    mockearHooks('admin')
    render(<Inventario />)
    const modal = abrirAjuste()

    fireEvent.change(modal.getByLabelText('Stock mínimo'), { target: { value: '7' } })
    fireEvent.click(modal.getByRole('button', { name: 'Guardar' }))
    fireEvent.click(screen.getByRole('button', { name: 'Volver' }))

    const formulario = within(screen.getByRole('dialog', { name: 'Ajustar inventario' }))
    expect(formulario.getByLabelText('Stock mínimo')).toHaveValue(7)
  })

  it('un error del backend se muestra dentro del modal sin cerrarlo', async () => {
    mockearHooks('admin')
    useAjustarInventarioMock.mockReturnValue({
      mutateAsync: vi.fn().mockRejectedValue({
        response: { data: { detail: 'El stock cambió a 1.00 mientras ajustabas; revísalo y vuelve a intentar.' } },
      }),
      isPending: false,
    } as unknown as ReturnType<typeof useAjustarInventario>)
    render(<Inventario />)
    const modal = abrirAjuste()

    fireEvent.change(modal.getByLabelText('Stock actual'), { target: { value: '3' } })
    fireEvent.change(modal.getByLabelText('Motivo del ajuste'), { target: { value: 'conteo_fisico' } })
    fireEvent.click(modal.getByRole('button', { name: 'Guardar' }))
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: 'Confirmar' }))
    })

    expect(screen.getByRole('dialog', { name: '¿Estás seguro?' })).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent('El stock cambió a 1.00')
  })

  it('el historial muestra el motivo de un ajuste', () => {
    mockearHooks()
    useMovimientosInventarioMock.mockReturnValue({
      data: [{ ...MOVIMIENTOS[0], id: 9, motivo: 'ajuste', tipo_movimiento: 'salida', observacion: 'Merma o daño: Frasco roto' }],
      isLoading: false,
    } as unknown as ReturnType<typeof useMovimientosInventario>)
    render(<Inventario />)
    fireEvent.click(screen.getByRole('tab', { name: 'Movimientos' }))

    expect(within(screen.getByRole('table')).getByText('Ajuste · Merma o daño: Frasco roto')).toBeInTheDocument()
  })
})

describe('Inventario — filtros de existencias', () => {
  const STOCK_VARIADO = [
    { id: 1, nombre: 'Suero', stock_actual: '2.00', stock_minimo: '10.00', stock_bajo: true },
    { id: 2, nombre: 'Gasa', stock_actual: '50.00', stock_minimo: '10.00', stock_bajo: false },
    { id: 3, nombre: 'Vendas', stock_actual: '0.00', stock_minimo: '0.00', stock_bajo: false },
    { id: 4, nombre: 'Guantes', stock_actual: '8.00', stock_minimo: '0.00', stock_bajo: false },
  ]

  function renderVariado() {
    mockearHooks()
    useStockMock.mockReturnValue({ data: STOCK_VARIADO, isLoading: false } as unknown as ReturnType<typeof useStock>)
    render(<Inventario />)
  }

  const nombres = () =>
    within(screen.getByRole('table'))
      .getAllByRole('row')
      .slice(1)
      .map((fila) => fila.querySelector('td')?.textContent)

  it('filtra por estado, incluido "Por reabastecer"', () => {
    renderVariado()

    fireEvent.change(screen.getByLabelText('Estado'), { target: { value: 'agotado' } })
    expect(nombres()).toEqual(['Vendas'])

    fireEvent.change(screen.getByLabelText('Estado'), { target: { value: 'porReabastecer' } })
    expect(nombres()).toEqual(['Suero', 'Vendas'])
  })

  it('filtra por stock mínimo definido o sin mínimo, y "Limpiar filtros" los quita', () => {
    renderVariado()

    fireEvent.change(screen.getByLabelText('Stock mínimo'), { target: { value: 'sinMinimo' } })
    expect(nombres()).toEqual(['Vendas', 'Guantes'])

    fireEvent.change(screen.getByLabelText('Estado'), { target: { value: 'enExistencia' } })
    expect(nombres()).toEqual(['Guantes'])

    fireEvent.click(screen.getByRole('button', { name: 'Limpiar filtros' }))
    expect(nombres()).toHaveLength(4)
    expect(screen.getByLabelText('Stock mínimo')).toHaveValue('')
  })

  it('sin coincidencias muestra el mensaje de filtros', () => {
    mockearHooks()
    render(<Inventario />)

    fireEvent.change(screen.getByLabelText('Estado'), { target: { value: 'agotado' } })
    expect(screen.getByText('Ningún ítem coincide con los filtros.')).toBeInTheDocument()
  })
})
