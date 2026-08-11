import styles from './Modal.module.css'

export function Modal({ titulo, abierto, onCerrar, children }) {
  if (!abierto) return null

  return (
    <div className={styles.overlay} onClick={onCerrar}>
      <div
        className={styles.contenido}
        onClick={(evento) => evento.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={titulo}
      >
        <div className={styles.encabezado}>
          <h2 className={styles.titulo}>{titulo}</h2>
          <button type="button" className={styles.botonCerrar} onClick={onCerrar} aria-label="Cerrar">
            ✕
          </button>
        </div>
        <div className={styles.cuerpo}>{children}</div>
      </div>
    </div>
  )
}
