import { useEffect, useRef, useState, type FocusEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import logoFlebosil from '../../assets/flebosil_transparentbg/logo_flebosil.png'
import { useAuth } from '../../context/AuthContext'
import { useNotificaciones } from '../../hooks/useNotificaciones'
import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import { Avatar } from '../common/Avatar'
import { Icono } from '../common/Icono'
import styles from './Header.module.css'

interface HeaderProps {
  onToggleSidebar: () => void
}

type Desplegable = 'notificaciones' | 'usuario'

// Convención de las campanas: a partir de 10 el número exacto deja de importar.
function textoContador(contador: number): string {
  return contador > 9 ? '9+' : String(contador)
}

export function Header({ onToggleSidebar }: HeaderProps) {
  const { data: usuario } = useUsuarioActual()
  // Secciones ya recortadas por rol en el backend (001, "Actualización:
  // centro de notificaciones y avisos por correo"): el operador recibe solo
  // sus ventas, compras y facturas, y nunca las nóminas.
  const { data: notificaciones, isLoading: notificacionesCargando } = useNotificaciones()
  // Un solo estado para los dos desplegables: abrir uno cierra el otro.
  const [desplegable, setDesplegable] = useState<Desplegable | null>(null)
  const notificacionesAbiertas = desplegable === 'notificaciones'
  const menuAbierto = desplegable === 'usuario'
  const contenedorNotificaciones = useRef<HTMLDivElement>(null)
  const contenedorUsuario = useRef<HTMLDivElement>(null)
  const botonNotificaciones = useRef<HTMLButtonElement>(null)
  const botonUsuario = useRef<HTMLButtonElement>(null)
  const { logout } = useAuth()
  const navigate = useNavigate()

  // Cierra el desplegable al cambiar de ruta (el Header no se vuelve a montar
  // al navegar). Se ajusta durante el render, sin un efecto extra. Cuenta
  // también la búsqueda: un enlace a /rrhh?pestana=nominas estando ya en
  // /rrhh también es una navegación.
  const { pathname, search } = useLocation()
  const ruta = pathname + search
  const [rutaActual, setRutaActual] = useState(ruta)
  if (ruta !== rutaActual) {
    setRutaActual(ruta)
    setDesplegable(null)
  }

  // Con un desplegable abierto: clic o toque fuera de él (y de su botón) lo
  // cierra sin bloquear ese clic, y Escape lo cierra devolviendo el foco a
  // su botón. Los oyentes solo existen mientras hay uno abierto.
  useEffect(() => {
    if (!desplegable) return
    const contenedorAbierto = (desplegable === 'notificaciones' ? contenedorNotificaciones : contenedorUsuario).current
    const botonAbierto = (desplegable === 'notificaciones' ? botonNotificaciones : botonUsuario).current

    function alPulsar(evento: PointerEvent) {
      if (!contenedorAbierto?.contains(evento.target as Node)) setDesplegable(null)
    }
    function alTeclear(evento: KeyboardEvent) {
      if (evento.key !== 'Escape') return
      setDesplegable(null)
      botonAbierto?.focus()
    }

    document.addEventListener('pointerdown', alPulsar)
    document.addEventListener('keydown', alTeclear)
    return () => {
      document.removeEventListener('pointerdown', alPulsar)
      document.removeEventListener('keydown', alTeclear)
    }
  }, [desplegable])

  function alternar(cual: Desplegable) {
    setDesplegable((actual) => (actual === cual ? null : cual))
  }

  // Cierre al salir el foco con el teclado. Sin `relatedTarget` (clic en una
  // zona sin controles dentro del desplegable) no se cierra: el clic fuera ya
  // lo cubre el oyente de arriba.
  function alPerderFoco(cual: Desplegable, evento: FocusEvent<HTMLDivElement>) {
    const siguiente = evento.relatedTarget
    if (siguiente && !evento.currentTarget.contains(siguiente)) {
      setDesplegable((actual) => (actual === cual ? null : actual))
    }
  }

  // Solo lo que requiere acción; lo demás se lista pero no suma.
  const contador = notificaciones?.contador ?? 0
  const secciones = notificaciones?.secciones ?? []

  function cerrarSesion() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className={styles.header}>
      <div className={styles.headerLeft}>
        <button
          type="button"
          className={styles.sidebarToggle}
          onClick={onToggleSidebar}
          aria-label="Mostrar u ocultar barra lateral"
        >
          <Icono nombre="menu" tamano={22} />
        </button>
        <Link to="/dashboard" className={styles.logo}>
          <img src={logoFlebosil} alt="FleboSil" className={styles.logoImage} />
        </Link>
      </div>

      <div className={styles.headerRight}>
        <div
          ref={contenedorNotificaciones}
          className={styles.notifications}
          onBlur={(evento) => alPerderFoco('notificaciones', evento)}
        >
          <button
            ref={botonNotificaciones}
            type="button"
            className={styles.notificationsButton}
            onClick={() => alternar('notificaciones')}
            aria-label={contador > 0 ? `Notificaciones: ${contador} requieren acción` : 'Notificaciones'}
            aria-haspopup="menu"
            aria-expanded={notificacionesAbiertas}
          >
            <Icono nombre="campana" tamano={20} />
            {contador > 0 && (
              <span className={styles.counter} aria-hidden="true">
                {textoContador(contador)}
              </span>
            )}
          </button>
          {notificacionesAbiertas && (
            <div className={`${styles.dropdown} ${styles.notificationsPanel}`} role="menu" aria-label="Notificaciones">
              {/* Mientras la petición no resuelve no se afirma "Todo al día":
                  sería contenido incorrecto, no un estado de carga. */}
              {notificacionesCargando ? (
                <p className={styles.dropdownEmpty}>Cargando notificaciones…</p>
              ) : secciones.length === 0 ? (
                <p className={styles.allClear}>Todo al día</p>
              ) : (
                secciones.map((seccion) => (
                  <section key={seccion.clave} className={styles.notificationGroup} aria-label={seccion.titulo}>
                    <p className={styles.dropdownSection}>
                      <span>{seccion.titulo}</span>
                      <span className={styles.sectionCount}>{seccion.total}</span>
                    </p>
                    <ul className={styles.notificationList}>
                      {seccion.elementos.map((elemento) => (
                        <li key={`${elemento.ruta}-${elemento.titulo}`}>
                          <Link
                            to={elemento.ruta}
                            className={
                              elemento.urgente
                                ? `${styles.notificationLink} ${styles.notificationUrgent}`
                                : styles.notificationLink
                            }
                          >
                            <strong>{elemento.titulo}</strong>
                            <span>{elemento.detalle}</span>
                            {elemento.etiqueta && (
                              <span className={elemento.urgente ? 'status statusWarning' : 'status statusPrimary'}>
                                {elemento.etiqueta}
                              </span>
                            )}
                          </Link>
                        </li>
                      ))}
                    </ul>
                    <Link
                      to={seccion.ruta}
                      className={`${styles.menuItem} ${styles.dropdownFooter}`}
                      aria-label={`Ver todas: ${seccion.titulo}`}
                    >
                      Ver todas
                    </Link>
                  </section>
                ))
              )}
            </div>
          )}
        </div>

        <div
          ref={contenedorUsuario}
          className={styles.userMenu}
          onBlur={(evento) => alPerderFoco('usuario', evento)}
        >
          <button
            ref={botonUsuario}
            type="button"
            className={styles.userButton}
            onClick={() => alternar('usuario')}
            aria-haspopup="menu"
            aria-expanded={menuAbierto}
          >
            <Avatar nombre={usuario?.nombre} foto={usuario?.foto_usuario} />
            <span className={styles.userData}>
              <span className={styles.userName}>{usuario?.nombre ?? '…'}</span>
              <span className={styles.userRole}>{usuario?.rol ?? ''}</span>
            </span>
            <span className={styles.caret} aria-hidden="true">
              ▾
            </span>
          </button>
          {menuAbierto && (
            <div className={styles.dropdown} role="menu">
              <Link to="/informacion-usuario" className={styles.menuItem}>
                Información de Usuario
              </Link>
              <button type="button" className={`${styles.menuItem} ${styles.menuItemDanger}`} onClick={cerrarSesion}>
                Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
