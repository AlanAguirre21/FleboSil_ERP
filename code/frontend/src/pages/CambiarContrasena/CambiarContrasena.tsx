import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

import { cambiarContrasena } from '../../api/auth'
import { useAuth } from '../../context/AuthContext'
import styles from './CambiarContrasena.module.css'

const MENSAJE_SIN_CONTEXTO =
  'Tu sesión de recuperación expiró o no es válida. Solicita un nuevo código.'
const MENSAJE_ERROR_GENERICO = 'No se pudo cambiar la contraseña. Intenta de nuevo.'

export function CambiarContrasena() {
  const location = useLocation()
  const navigate = useNavigate()
  const { iniciarSesionConTokens } = useAuth()
  const email = location.state?.email

  const [password, setPassword] = useState('')
  const [confirmacion, setConfirmacion] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  if (!email) {
    return (
      <Navigate to="/recuperar-contrasena" replace state={{ mensaje: MENSAJE_SIN_CONTEXTO }} />
    )
  }

  async function alEnviar(evento) {
    evento.preventDefault()
    setError('')

    if (!password || !confirmacion) {
      setError('Completa ambos campos de contraseña.')
      return
    }

    if (password !== confirmacion) {
      setError('Las contraseñas no coinciden.')
      return
    }

    setCargando(true)
    try {
      const { access, refresh } = await cambiarContrasena(email, password, confirmacion)
      iniciarSesionConTokens(access, refresh)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      const datos = err.response?.data
      setError(
        datos?.detail ??
          datos?.password?.[0] ??
          datos?.password_confirmacion?.[0] ??
          MENSAJE_ERROR_GENERICO,
      )
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className={styles.pagina}>
      <form className={styles.formulario} onSubmit={alEnviar} noValidate>
        <div className={styles.encabezado}>
          <h1 className={styles.logoTexto}>FleboSil</h1>
          <p className={styles.subtitulo}>Nueva contraseña</p>
        </div>

        <label className={styles.campo}>
          Nueva contraseña
          <input
            type="password"
            value={password}
            onChange={(evento) => setPassword(evento.target.value)}
            autoComplete="new-password"
            required
          />
        </label>

        <label className={styles.campo}>
          Confirmar nueva contraseña
          <input
            type="password"
            value={confirmacion}
            onChange={(evento) => setConfirmacion(evento.target.value)}
            autoComplete="new-password"
            required
          />
        </label>

        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}

        <button type="submit" className={styles.boton} disabled={cargando}>
          {cargando ? 'Guardando…' : 'Guardar nueva contraseña'}
        </button>
      </form>
    </div>
  )
}
