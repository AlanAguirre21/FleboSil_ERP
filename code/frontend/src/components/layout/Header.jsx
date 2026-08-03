import { useState } from 'react'
import { Link } from 'react-router-dom'

import { clearToken } from '../../api/client'
import { useAlertasStock } from '../../hooks/useAlertasStock'
import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import styles from './Header.module.css'

export function Header({ onToggleSidebar }) {
  const { data: usuario } = useUsuarioActual()
  const { data: alertas, isLoading: alertasCargando } = useAlertasStock()
  const [notificacionesAbiertas, setNotificacionesAbiertas] = useState(false)
  const [menuAbierto, setMenuAbierto] = useState(false)

  const totalAlertas = alertas?.length ?? 0

  function cerrarSesion() {
    clearToken()
    window.location.assign('/')
  }

  return (
    <header className={styles.header}>
      <div className={styles.izquierda}>
        <button
          type="button"
          className={styles.botonSidebar}
          onClick={onToggleSidebar}
          aria-label="Mostrar u ocultar barra lateral"
        >
          ☰
        </button>
        <Link to="/dashboard" className={styles.logo}>
          <span className={styles.logoTexto}>FleboSil</span>
          <span className={styles.subtitulo}>Enterprise Manager</span>
        </Link>
      </div>

      <div className={styles.derecha}>
        <div className={styles.notificaciones}>
          <button
            type="button"
            className={styles.botonNotificaciones}
            onClick={() => setNotificacionesAbiertas((abierto) => !abierto)}
            aria-label="Alertas de stock"
          >
            🔔
            {totalAlertas > 0 && (
              <span className={styles.contador}>{totalAlertas}</span>
            )}
          </button>
          {notificacionesAbiertas && (
            <div className={styles.dropdown} role="menu">
              {/* Mientras la petición no resuelve no se afirma "sin alertas":
                  sería contenido incorrecto, no un estado de carga. */}
              {alertasCargando ? (
                <p className={styles.dropdownVacio}>Cargando alertas…</p>
              ) : totalAlertas === 0 ? (
                <p className={styles.dropdownVacio}>Sin alertas de stock</p>
              ) : (
                <ul className={styles.listaAlertas}>
                  {alertas.map((alerta) => (
                    <li key={`${alerta.tipo}-${alerta.nombre}-${alerta.sucursal}`}>
                      <strong>{alerta.nombre}</strong>
                      <span>{alerta.sucursal}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        <div className={styles.usuario}>
          <button
            type="button"
            className={styles.botonUsuario}
            onClick={() => setMenuAbierto((abierto) => !abierto)}
          >
            <span className={styles.nombreUsuario}>{usuario?.nombre ?? '…'}</span>
            <span className={styles.rolUsuario}>{usuario?.rol ?? ''}</span>
          </button>
          {menuAbierto && (
            <div className={styles.dropdown} role="menu">
              <Link to="/informacion-usuario" className={styles.itemMenu}>
                Información de Usuario
              </Link>
              <button type="button" className={styles.itemMenu} onClick={cerrarSesion}>
                Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
