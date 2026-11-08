import { useEffect, useId, useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'

import styles from './Modal.module.css'

interface ModalProps {
  titulo: string
  // Texto de la barra del modal cuando debe diferir del nombre accesible (`titulo`).
  tituloVisible?: string
  // Línea opcional bajo el título que explica para qué es el modal.
  descripcion?: string
  abierto: boolean
  onCerrar: () => void
  children: ReactNode
  // 'amplio' para formularios con tablas de líneas (ej. traslados); 'normal' por defecto.
  ancho?: 'normal' | 'amplio'
}

const SELECTOR_ENFOCABLE = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled]):not([type="hidden"])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',')

// Modales abiertos, del más antiguo al más reciente: Escape y el ciclo de Tab
// solo actúan sobre el de arriba (ej. una confirmación abierta sobre una ficha).
const pilaModales: symbol[] = []
// `overflow` de <body> antes de abrir el primer modal, para restaurarlo al
// cerrar el último (un modal abierto sobre otro no lo vuelve a guardar).
let overflowOriginal = ''

function enfocables(contenedor: HTMLElement): HTMLElement[] {
  return [...contenedor.querySelectorAll<HTMLElement>(SELECTOR_ENFOCABLE)].filter(
    (el) => !el.closest('[hidden]') && el.getAttribute('aria-hidden') !== 'true',
  )
}

/**
 * Diálogo modal según el patrón de WAI-ARIA: se dibuja sobre toda la app (portal
 * en `body`), lleva el foco al primer control del contenido, lo mantiene dentro
 * con Tab/Shift+Tab, se cierra con Escape, con la ✕ o con un clic en el fondo, y
 * al cerrarse devuelve el foco al botón que lo abrió.
 */
export function Modal(props: ModalProps) {
  if (!props.abierto) return null
  return <ModalAbierto {...props} />
}

function ModalAbierto({ titulo, tituloVisible, descripcion, onCerrar, children, ancho = 'normal' }: ModalProps) {
  const dialogoRef = useRef<HTMLDivElement>(null)
  const onCerrarRef = useRef(onCerrar)
  const pulsoEnFondo = useRef(false)
  const idTitulo = useId()
  const idDescripcion = useId()

  useEffect(() => {
    onCerrarRef.current = onCerrar
  }, [onCerrar])

  useEffect(() => {
    const clave = Symbol('modal')
    if (pilaModales.length === 0) {
      overflowOriginal = document.body.style.overflow
      document.body.style.overflow = 'hidden'
    }
    pilaModales.push(clave)
    const enfocadoAntes = document.activeElement as HTMLElement | null
    const dialogo = dialogoRef.current

    // Foco inicial: el primer control del contenido (no la ✕ del encabezado);
    // en una confirmación es "Cancelar", la opción menos destructiva.
    if (dialogo) {
      const cuerpo = dialogo.querySelector<HTMLElement>('[data-modal-cuerpo]')
      const primero = (cuerpo && enfocables(cuerpo)[0]) ?? dialogo
      primero.focus()
    }

    function alPresionarTecla(evento: KeyboardEvent) {
      if (pilaModales[pilaModales.length - 1] !== clave || !dialogo) return
      if (evento.key === 'Escape') {
        evento.stopPropagation()
        onCerrarRef.current()
        return
      }
      if (evento.key !== 'Tab') return
      const lista = enfocables(dialogo)
      if (lista.length === 0) {
        evento.preventDefault()
        return
      }
      const primero = lista[0]!
      const ultimo = lista[lista.length - 1]!
      if (evento.shiftKey && document.activeElement === primero) {
        evento.preventDefault()
        ultimo.focus()
      } else if (!evento.shiftKey && document.activeElement === ultimo) {
        evento.preventDefault()
        primero.focus()
      } else if (!dialogo.contains(document.activeElement)) {
        evento.preventDefault()
        primero.focus()
      }
    }

    document.addEventListener('keydown', alPresionarTecla)

    return () => {
      document.removeEventListener('keydown', alPresionarTecla)
      pilaModales.splice(pilaModales.indexOf(clave), 1)
      if (pilaModales.length === 0) document.body.style.overflow = overflowOriginal
      // Devolver el foco a quien abrió el modal, si sigue en la página.
      if (enfocadoAntes && document.contains(enfocadoAntes)) enfocadoAntes.focus()
    }
  }, [])

  return createPortal(
    <div
      className={styles.overlay}
      // Solo cierra si el clic empezó y terminó en el fondo: arrastrar al
      // seleccionar texto de un campo hasta fuera del diálogo no lo cierra.
      onMouseDown={(evento) => {
        pulsoEnFondo.current = evento.target === evento.currentTarget
      }}
      onClick={(evento) => {
        evento.stopPropagation()
        if (pulsoEnFondo.current && evento.target === evento.currentTarget) onCerrar()
        pulsoEnFondo.current = false
      }}
    >
      <div
        ref={dialogoRef}
        className={ancho === 'amplio' ? `${styles.dialog} ${styles.dialogWide}` : styles.dialog}
        onClick={(evento) => evento.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={titulo}
        aria-describedby={descripcion ? idDescripcion : undefined}
        tabIndex={-1}
      >
        <header className={styles.dialogHeader}>
          <div className={styles.dialogHeading}>
            <h2 id={idTitulo} className={styles.dialogTitle}>
              {tituloVisible ?? titulo}
            </h2>
            {descripcion && (
              <p id={idDescripcion} className={styles.dialogDescription}>
                {descripcion}
              </p>
            )}
          </div>
          <button type="button" className={styles.closeButton} onClick={onCerrar} aria-label="Cerrar">
            <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </header>
        <div className={styles.dialogBody} data-modal-cuerpo>
          {children}
        </div>
      </div>
    </div>,
    document.body,
  )
}
