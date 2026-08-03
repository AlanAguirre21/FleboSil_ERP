import { NavLink } from 'react-router-dom'

import styles from './Sidebar.module.css'

export function Sidebar({ modulos, colapsado }) {
  return (
    <aside className={`${styles.sidebar} ${colapsado ? styles.colapsado : ''}`}>
      <nav>
        <ul className={styles.lista}>
          {modulos.map((modulo) => (
            <li key={modulo.slug}>
              <NavLink
                to={modulo.ruta}
                className={({ isActive }) =>
                  isActive ? `${styles.enlace} ${styles.activo}` : styles.enlace
                }
              >
                {modulo.nombre}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  )
}
