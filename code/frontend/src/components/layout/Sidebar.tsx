import { NavLink } from 'react-router-dom'

import type { ModuloMenu } from '../../api/usuarios'
import styles from './Sidebar.module.css'

interface SidebarProps {
  modulos: ModuloMenu[]
  colapsado: boolean
}

export function Sidebar({ modulos, colapsado }: SidebarProps) {
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
