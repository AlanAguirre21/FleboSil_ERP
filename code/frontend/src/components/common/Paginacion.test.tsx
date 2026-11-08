import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { normalizarBusqueda, paginasVisibles } from '../../hooks/usePaginacion'
import { Tabla, type ColumnaTabla } from './Tabla'

interface Persona {
  id: number
  nombre: string
  activo: boolean
}

const COLUMNAS: ColumnaTabla<Persona>[] = [
  { clave: 'nombre', encabezado: 'Nombre' },
  {
    clave: 'activo',
    encabezado: 'Estado',
    render: (fila) => <span className="status">{fila.activo ? 'Activo' : 'Inactivo'}</span>,
  },
]

function personas(cantidad: number): Persona[] {
  return Array.from({ length: cantidad }, (_, i) => ({ id: i + 1, nombre: `Persona ${i + 1}`, activo: i % 2 === 0 }))
}

const filasCuerpo = (container: HTMLElement) => container.querySelectorAll('tbody tr').length

describe('Tabla — paginación y búsqueda', () => {
  it('muestra 10 filas por defecto y una página por cada 10', () => {
    const { container } = render(<Tabla columnas={COLUMNAS} datos={personas(35)} />)

    expect(filasCuerpo(container)).toBe(10)
    expect(screen.getByText('Mostrando 1–10 de 35')).toBeInTheDocument()
    for (const pagina of [1, 2, 3, 4]) {
      expect(screen.getByRole('button', { name: `Página ${pagina}` })).toBeInTheDocument()
    }
    expect(screen.getByRole('button', { name: 'Anterior' })).toBeDisabled()
  })

  it('navega entre páginas con los números, Siguiente y Anterior', () => {
    const { container } = render(<Tabla columnas={COLUMNAS} datos={personas(35)} />)

    fireEvent.click(screen.getByRole('button', { name: 'Página 4' }))
    expect(filasCuerpo(container)).toBe(5)
    expect(screen.getByText('Persona 31')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Siguiente' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Página 4' })).toHaveAttribute('aria-current', 'page')

    fireEvent.click(screen.getByRole('button', { name: 'Anterior' }))
    expect(screen.getByText('Mostrando 21–30 de 35')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Siguiente' }))
    expect(screen.getByText('Mostrando 31–35 de 35')).toBeInTheDocument()
  })

  it('ofrece 10, 25, 50, 100 y Todas, y al cambiar vuelve a la página 1', () => {
    const { container } = render(<Tabla columnas={COLUMNAS} datos={personas(120)} />)
    const selector = screen.getByLabelText('Filas por página')

    expect([...selector.querySelectorAll('option')].map((o) => o.textContent)).toEqual([
      '10',
      '25',
      '50',
      '100',
      'Todas',
    ])

    fireEvent.click(screen.getByRole('button', { name: 'Página 2' }))
    for (const [valor, esperado] of [
      ['25', 25],
      ['50', 50],
      ['100', 100],
      ['todas', 120],
    ] as const) {
      fireEvent.change(selector, { target: { value: valor } })
      expect(filasCuerpo(container)).toBe(esperado)
      expect(screen.getByText(`Mostrando 1–${esperado} de 120`)).toBeInTheDocument()
    }
    expect(screen.queryByRole('navigation', { name: 'Paginación' })).not.toBeInTheDocument()
  })

  it('con muchas páginas resume los números con puntos suspensivos', () => {
    render(<Tabla columnas={COLUMNAS} datos={personas(200)} />)

    expect(screen.getByRole('button', { name: 'Página 20' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Página 10' })).not.toBeInTheDocument()
    expect(screen.getByText('…')).toBeInTheDocument()
  })

  it('busca sin distinguir mayúsculas ni acentos, también en el texto que muestra el render', () => {
    const datos = [
      { id: 1, nombre: 'José Pérez', activo: true },
      { id: 2, nombre: 'Ana López', activo: false },
    ]
    const { container } = render(<Tabla columnas={COLUMNAS} datos={datos} />)
    const buscador = screen.getByLabelText('Buscar en la tabla')

    fireEvent.change(buscador, { target: { value: 'JOSE perez' } })
    expect(filasCuerpo(container)).toBe(1)
    expect(screen.getByText('José Pérez')).toBeInTheDocument()

    fireEvent.change(buscador, { target: { value: 'inactivo' } })
    expect(filasCuerpo(container)).toBe(1)
    expect(screen.getByText('Ana López')).toBeInTheDocument()
    expect(screen.getByText('Mostrando 1–1 de 1 (de 2 en total)')).toBeInTheDocument()
  })

  it('al buscar vuelve a la página 1 y sin coincidencias muestra su propio mensaje', () => {
    const { container } = render(<Tabla columnas={COLUMNAS} datos={personas(35)} mensajeVacio="Vacío" />)

    fireEvent.click(screen.getByRole('button', { name: 'Página 3' }))
    fireEvent.change(screen.getByLabelText('Buscar en la tabla'), { target: { value: 'Persona 1' } })
    // "Persona 1" y "Persona 10" … "Persona 19": 11 coincidencias, desde la página 1.
    expect(screen.getByText('Mostrando 1–10 de 11 (de 35 en total)')).toBeInTheDocument()

    fireEvent.change(screen.getByLabelText('Buscar en la tabla'), { target: { value: 'nadie' } })
    expect(filasCuerpo(container)).toBe(0)
    expect(screen.getByText('Ninguna fila coincide con la búsqueda.')).toBeInTheDocument()
    expect(screen.queryByText('Vacío')).not.toBeInTheDocument()
  })

  it('textoBusqueda permite buscar por un dato que la celda no muestra como texto', () => {
    const columnas: ColumnaTabla<Persona>[] = [
      { clave: 'nombre', encabezado: 'Nombre' },
      {
        clave: 'activo',
        encabezado: 'Estado',
        render: () => <i aria-label="icono" />,
        textoBusqueda: (fila) => (fila.activo ? 'vigente' : 'baja'),
      },
    ]
    const { container } = render(<Tabla columnas={columnas} datos={personas(4)} />)

    fireEvent.change(screen.getByLabelText('Buscar en la tabla'), { target: { value: 'baja' } })
    expect(filasCuerpo(container)).toBe(2)
  })

  it('buscador={false} oculta el buscador pero conserva filas por página y paginación', () => {
    render(<Tabla columnas={COLUMNAS} datos={personas(15)} buscador={false} />)

    expect(screen.queryByLabelText('Buscar en la tabla')).not.toBeInTheDocument()
    expect(screen.getByLabelText('Filas por página')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Página 2' })).toBeInTheDocument()
  })

  it('si los datos se reducen y la página ya no existe, muestra la última que sí existe', () => {
    const { container, rerender } = render(<Tabla columnas={COLUMNAS} datos={personas(35)} />)
    fireEvent.click(screen.getByRole('button', { name: 'Página 4' }))

    rerender(<Tabla columnas={COLUMNAS} datos={personas(12)} />)
    expect(filasCuerpo(container)).toBe(2)
    expect(screen.getByText('Mostrando 11–12 de 12')).toBeInTheDocument()
  })

  it('sin datos no muestra buscador ni paginación, solo el mensaje vacío', () => {
    render(<Tabla columnas={COLUMNAS} datos={[]} mensajeVacio="Nada todavía" />)

    expect(screen.queryByLabelText('Buscar en la tabla')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Filas por página')).not.toBeInTheDocument()
    expect(screen.queryByText(/Mostrando/)).not.toBeInTheDocument()
    expect(screen.getByText('Nada todavía')).toBeInTheDocument()
  })

  it('la fila de detalle solo acompaña a las filas de la página visible', () => {
    render(
      <Tabla
        columnas={COLUMNAS}
        datos={personas(12)}
        renderExpandido={(fila) => (fila.id === 11 ? <p>Detalle 11</p> : null)}
      />,
    )

    expect(screen.queryByText('Detalle 11')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Página 2' }))
    expect(screen.getByText('Detalle 11')).toBeInTheDocument()
  })
})

describe('paginasVisibles', () => {
  it('muestra todas cuando son pocas', () => {
    expect(paginasVisibles(1, 5)).toEqual([1, 2, 3, 4, 5])
  })

  it('primera, última, dos a cada lado de la actual y huecos', () => {
    expect(paginasVisibles(10, 20)).toEqual([1, null, 8, 9, 10, 11, 12, null, 20])
    expect(paginasVisibles(1, 20)).toEqual([1, 2, 3, null, 20])
    expect(paginasVisibles(20, 20)).toEqual([1, null, 18, 19, 20])
  })
})

describe('normalizarBusqueda', () => {
  it('quita acentos, mayúsculas y espacios de los extremos', () => {
    expect(normalizarBusqueda('  Ñandú CAMIÓN ')).toBe('nandu camion')
  })
})
