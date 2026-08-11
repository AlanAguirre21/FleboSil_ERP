import styles from './BotonPrimario.module.css'

const CLASES_POR_VARIANTE = {
  primario: 'primario',
  secundario: 'secundario',
  peligro: 'peligro',
}

export function BotonPrimario({ children, variante = 'primario', type = 'button', ...props }) {
  return (
    <button type={type} className={styles[CLASES_POR_VARIANTE[variante]]} {...props}>
      {children}
    </button>
  )
}
