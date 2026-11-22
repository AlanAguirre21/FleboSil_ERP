import { useEffect, useId, useRef, useState } from 'react'

import styles from './AyudaInfo.module.css'

interface AyudaInfoProps {
  texto: string
  // Nombre accesible del botón (por defecto, "Más información").
  etiqueta?: string
  // Hacia dónde se abre el globo desde el icono, para no salirse de la pantalla.
  alineacion?: 'izquierda' | 'derecha'
}

// Icono "i" con un globo de ayuda breve (patrón "toggletip"): se asoma al
// pasar el cursor y se abre o cierra con clic, toque, Enter o Espacio.
// Escape, perder el foco o un clic fuera lo cierran.
export function AyudaInfo({ texto, etiqueta = 'Más información', alineacion = 'izquierda' }: AyudaInfoProps) {
  const id = useId()
  const [abierto, setAbierto] = useState(false)
  const contenedor = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    if (!abierto) return
    const cerrarSiEsFuera = (evento: PointerEvent) => {
      if (!contenedor.current?.contains(evento.target as Node)) setAbierto(false)
    }
    document.addEventListener('pointerdown', cerrarSiEsFuera)
    return () => document.removeEventListener('pointerdown', cerrarSiEsFuera)
  }, [abierto])

  const clases = [styles.tooltip, alineacion === 'derecha' && styles.tooltipRight, abierto && styles.tooltipOpen]
    .filter(Boolean)
    .join(' ')

  return (
    <span className={styles.wrapper} ref={contenedor}>
      <button
        type="button"
        className={styles.trigger}
        aria-label={etiqueta}
        aria-describedby={id}
        aria-expanded={abierto}
        onClick={() => setAbierto((valor) => !valor)}
        onBlur={() => setAbierto(false)}
        onKeyDown={(evento) => {
          if (evento.key === 'Escape') setAbierto(false)
        }}
      >
        i
      </button>
      <span role="tooltip" id={id} className={clases}>
        {texto}
      </span>
    </span>
  )
}
