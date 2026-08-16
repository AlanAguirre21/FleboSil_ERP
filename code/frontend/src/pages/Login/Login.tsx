import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'
import styles from './Login.module.css'

const MENSAJE_ERROR_PREDETERMINADO = 'Correo o contraseña incorrectos.'
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function alEnviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setError('')

    if (!email.trim()) {
      setError('Ingresa tu correo electrónico.')
      return
    }
    if (!EMAIL_REGEX.test(email)) {
      setError('Ingresa un correo electrónico válido.')
      return
    }
    if (!password) {
      setError('Ingresa tu contraseña.')
      return
    }

    setCargando(true)

    try {
      await login(email, password)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      const detalle =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined
      setError(detalle ?? MENSAJE_ERROR_PREDETERMINADO)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className={styles.pagina}>
      <form className={styles.formulario} onSubmit={alEnviar} noValidate>
        <div className={styles.encabezado}>
          <h1 className={styles.logoTexto}>FleboSil</h1>
          <p className={styles.subtitulo}>Enterprise Manager</p>
        </div>

        <label className={styles.campo}>
          Correo electrónico
          <input
            type="email"
            value={email}
            onChange={(evento) => setEmail(evento.target.value)}
            autoComplete="username"
            required
          />
        </label>

        <label className={styles.campo}>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(evento) => setPassword(evento.target.value)}
            autoComplete="current-password"
            required
          />
        </label>

        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}

        <button type="submit" className={styles.boton} disabled={cargando}>
          {cargando ? 'Ingresando…' : 'Ingresar'}
        </button>

        <Link to="/recuperar-contrasena" className={styles.enlace}>
          ¿Olvidaste tu contraseña?
        </Link>
      </form>
    </div>
  )
}
