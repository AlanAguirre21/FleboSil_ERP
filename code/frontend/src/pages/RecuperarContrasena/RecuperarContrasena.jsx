import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { solicitarRecuperacion, verificarCodigo } from '../../api/auth'
import styles from './RecuperarContrasena.module.css'

const MENSAJE_ENVIO_GENERICO = 'Si el correo está registrado, te enviamos un código de verificación.'
const MENSAJE_ERROR_CODIGO = 'Código inválido o expirado.'
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function RecuperarContrasena() {
  const location = useLocation()
  const [paso, setPaso] = useState('correo')
  const [email, setEmail] = useState('')
  const [codigo, setCodigo] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState(location.state?.mensaje ?? '')
  const [cargando, setCargando] = useState(false)
  const navigate = useNavigate()

  async function enviarCodigo() {
    try {
      const { detail } = await solicitarRecuperacion(email)
      setMensaje(detail ?? MENSAJE_ENVIO_GENERICO)
    } catch {
      setMensaje(MENSAJE_ENVIO_GENERICO)
    }
  }

  async function alEnviarCorreo(evento) {
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

    setCargando(true)
    await enviarCodigo()
    setCargando(false)
    setPaso('codigo')
  }

  async function alReenviar() {
    setError('')
    setCargando(true)
    await enviarCodigo()
    setCargando(false)
  }

  async function alVerificarCodigo(evento) {
    evento.preventDefault()
    setError('')

    if (codigo.length !== 6) {
      setError('Ingresa el código de 6 dígitos.')
      return
    }

    setCargando(true)
    try {
      await verificarCodigo(email, codigo)
      navigate('/cambiar-contrasena', { replace: true, state: { email } })
    } catch (err) {
      setError(err.response?.data?.detail ?? MENSAJE_ERROR_CODIGO)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className={styles.pagina}>
      {paso === 'correo' ? (
        <form className={styles.formulario} onSubmit={alEnviarCorreo} noValidate>
          <div className={styles.encabezado}>
            <h1 className={styles.logoTexto}>FleboSil</h1>
            <p className={styles.subtitulo}>Recuperar contraseña</p>
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

          {error && (
            <p className={styles.error} role="alert">
              {error}
            </p>
          )}

          <button type="submit" className={styles.boton} disabled={cargando}>
            {cargando ? 'Enviando…' : 'Enviar código'}
          </button>

          <Link to="/login" className={styles.enlace}>
            Volver a iniciar sesión
          </Link>
        </form>
      ) : (
        <form className={styles.formulario} onSubmit={alVerificarCodigo} noValidate>
          <div className={styles.encabezado}>
            <h1 className={styles.logoTexto}>FleboSil</h1>
            <p className={styles.subtitulo}>Verifica tu código</p>
          </div>

          {mensaje && <p className={styles.mensaje}>{mensaje}</p>}

          <label className={styles.campo}>
            Código de 6 dígitos
            <input
              type="text"
              inputMode="numeric"
              className={styles.inputCodigo}
              maxLength={6}
              value={codigo}
              onChange={(evento) => setCodigo(evento.target.value.replace(/\D/g, ''))}
              required
            />
          </label>

          {error && (
            <p className={styles.error} role="alert">
              {error}
            </p>
          )}

          <button
            type="submit"
            className={styles.boton}
            disabled={cargando || codigo.length !== 6}
          >
            {cargando ? 'Verificando…' : 'Verificar código'}
          </button>

          <button
            type="button"
            className={styles.enlaceBoton}
            onClick={alReenviar}
            disabled={cargando}
          >
            Reenviar código
          </button>

          <Link to="/login" className={styles.enlace}>
            Volver a iniciar sesión
          </Link>
        </form>
      )}
    </div>
  )
}
