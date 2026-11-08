import { fireEvent, render, screen } from '@testing-library/react'
import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'

import { Modal } from './Modal'

function Formulario({ onCerrar = vi.fn() }: { onCerrar?: () => void }) {
  return (
    <Modal titulo="Nuevo producto" descripcion="Datos del catálogo." abierto onCerrar={onCerrar}>
      <form className="form">
        <label className="field">
          Nombre
          <input type="text" />
        </label>
        <div className="formActions">
          <button type="button">Cancelar</button>
          <button type="submit">Guardar</button>
        </div>
      </form>
    </Modal>
  )
}

// Botón que abre el modal, para probar el foco de ida y vuelta.
function ConDisparador() {
  const [abierto, setAbierto] = useState(false)
  return (
    <>
      <button type="button" onClick={() => setAbierto(true)}>
        Abrir
      </button>
      <Modal titulo="Confirmar" abierto={abierto} onCerrar={() => setAbierto(false)}>
        <p className="confirmText">¿Seguro?</p>
        <div className="formActions">
          <button type="button" onClick={() => setAbierto(false)}>
            Cancelar
          </button>
          <button type="button">Desactivar</button>
        </div>
      </Modal>
    </>
  )
}

describe('Modal', () => {
  it('cerrado no dibuja nada', () => {
    render(
      <Modal titulo="X" abierto={false} onCerrar={vi.fn()}>
        contenido
      </Modal>,
    )
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('es un diálogo modal con nombre y descripción accesibles, dibujado sobre toda la app', () => {
    const { container } = render(<Formulario />)
    const dialogo = screen.getByRole('dialog', { name: 'Nuevo producto' })

    expect(dialogo).toHaveAttribute('aria-modal', 'true')
    expect(dialogo).toHaveAccessibleDescription('Datos del catálogo.')
    expect(container).not.toContainElement(dialogo) // portal en <body>
    expect(screen.getByRole('heading', { name: 'Nuevo producto' })).toBeInTheDocument()
  })

  it('al abrir enfoca el primer control del contenido, no la ✕', () => {
    render(<Formulario />)
    expect(screen.getByLabelText('Nombre')).toHaveFocus()
  })

  it('en una confirmación el foco inicial es "Cancelar", y al cerrar vuelve al botón que la abrió', () => {
    render(<ConDisparador />)
    const disparador = screen.getByRole('button', { name: 'Abrir' })
    disparador.focus()
    fireEvent.click(disparador)

    expect(screen.getByRole('button', { name: 'Cancelar' })).toHaveFocus()
    fireEvent.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(disparador).toHaveFocus()
  })

  it('Tab y Shift+Tab no salen del diálogo', () => {
    render(<Formulario />)
    const guardar = screen.getByRole('button', { name: 'Guardar' })
    const cerrar = screen.getByRole('button', { name: 'Cerrar' })

    guardar.focus()
    fireEvent.keyDown(document, { key: 'Tab' })
    expect(cerrar).toHaveFocus()

    fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })
    expect(guardar).toHaveFocus()
  })

  it('Escape, la ✕ y un clic en el fondo lo cierran', () => {
    const onCerrar = vi.fn()
    render(<Formulario onCerrar={onCerrar} />)

    fireEvent.keyDown(document, { key: 'Escape' })
    fireEvent.click(screen.getByRole('button', { name: 'Cerrar' }))
    const fondo = screen.getByRole('dialog').parentElement as HTMLElement
    fireEvent.mouseDown(fondo)
    fireEvent.click(fondo)

    expect(onCerrar).toHaveBeenCalledTimes(3)
  })

  it('un clic dentro del diálogo, o arrastrar desde dentro hasta el fondo, no lo cierra', () => {
    const onCerrar = vi.fn()
    render(<Formulario onCerrar={onCerrar} />)
    const dialogo = screen.getByRole('dialog')

    fireEvent.click(screen.getByLabelText('Nombre'))
    // Selección de texto que empieza en el campo y termina en el fondo.
    fireEvent.mouseDown(screen.getByLabelText('Nombre'))
    fireEvent.click(dialogo.parentElement as HTMLElement)

    expect(onCerrar).not.toHaveBeenCalled()
  })

  it('con dos modales abiertos, Escape solo cierra el de arriba', () => {
    const cerrarFicha = vi.fn()
    const cerrarConfirmacion = vi.fn()
    render(
      <>
        <Modal titulo="Ficha" abierto onCerrar={cerrarFicha}>
          <button type="button">Editar</button>
        </Modal>
        <Modal titulo="Confirmación" abierto onCerrar={cerrarConfirmacion}>
          <button type="button">Aceptar</button>
        </Modal>
      </>,
    )

    fireEvent.keyDown(document, { key: 'Escape' })
    expect(cerrarConfirmacion).toHaveBeenCalledTimes(1)
    expect(cerrarFicha).not.toHaveBeenCalled()
  })

  it('bloquea el desplazamiento de la página mientras está abierto', () => {
    const { unmount } = render(<Formulario />)
    expect(document.body.style.overflow).toBe('hidden')
    unmount()
    expect(document.body.style.overflow).toBe('')
  })

  it('con dos modales abiertos, el desplazamiento vuelve solo al cerrar el último', () => {
    const { rerender } = render(
      <>
        <Modal titulo="A" abierto onCerrar={vi.fn()}>a</Modal>
        <Modal titulo="B" abierto onCerrar={vi.fn()}>b</Modal>
      </>,
    )
    rerender(
      <>
        <Modal titulo="A" abierto onCerrar={vi.fn()}>a</Modal>
        <Modal titulo="B" abierto={false} onCerrar={vi.fn()}>b</Modal>
      </>,
    )
    expect(document.body.style.overflow).toBe('hidden')
    rerender(
      <>
        <Modal titulo="A" abierto={false} onCerrar={vi.fn()}>a</Modal>
        <Modal titulo="B" abierto={false} onCerrar={vi.fn()}>b</Modal>
      </>,
    )
    expect(document.body.style.overflow).toBe('')
  })
})
