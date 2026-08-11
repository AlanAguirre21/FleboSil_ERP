import { useState } from 'react'

import { BotonPrimario } from '../../components/common/BotonPrimario'
import { Modal } from '../../components/common/Modal'
import { Tabla } from '../../components/common/Tabla'
import { useCrearSucursal, useDesactivarSucursal, useEditarSucursal, useSucursales } from '../../hooks/useSucursales'
import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import styles from './Sucursales.module.css'

const SUCURSAL_VACIA = { nombre_sucursal: '', ubicacion_sucursal: '', telefono_sucursal: '' }

export function Sucursales() {
  const { data: usuario } = useUsuarioActual()
  const { data: sucursales, isLoading } = useSucursales()
  const crear = useCrearSucursal()
  const editar = useEditarSucursal()
  const desactivar = useDesactivarSucursal()

  const [formularioAbierto, setFormularioAbierto] = useState(false)
  const [sucursalEnEdicion, setSucursalEnEdicion] = useState(null)
  const [valores, setValores] = useState(SUCURSAL_VACIA)
  const [errorFormulario, setErrorFormulario] = useState('')
  const [sucursalADesactivar, setSucursalADesactivar] = useState(null)

  const esAdmin = usuario?.rol === 'admin'

  function abrirCrear() {
    setSucursalEnEdicion(null)
    setValores(SUCURSAL_VACIA)
    setErrorFormulario('')
    setFormularioAbierto(true)
  }

  function abrirEditar(sucursal) {
    setSucursalEnEdicion(sucursal)
    setValores({
      nombre_sucursal: sucursal.nombre_sucursal,
      ubicacion_sucursal: sucursal.ubicacion_sucursal,
      telefono_sucursal: sucursal.telefono_sucursal,
    })
    setErrorFormulario('')
    setFormularioAbierto(true)
  }

  function cerrarFormulario() {
    setFormularioAbierto(false)
  }

  async function alGuardar(evento) {
    evento.preventDefault()
    setErrorFormulario('')

    if (!valores.nombre_sucursal.trim()) {
      setErrorFormulario('Ingresa el nombre de la sucursal.')
      return
    }

    try {
      if (sucursalEnEdicion) {
        await editar.mutateAsync({ id: sucursalEnEdicion.id, datos: valores })
      } else {
        await crear.mutateAsync(valores)
      }
      setFormularioAbierto(false)
    } catch (err) {
      const datos = err.response?.data
      setErrorFormulario(
        datos?.detail ?? datos?.nombre_sucursal?.[0] ?? 'No se pudo guardar la sucursal. Intenta de nuevo.',
      )
    }
  }

  async function confirmarDesactivar() {
    await desactivar.mutateAsync(sucursalADesactivar.id)
    setSucursalADesactivar(null)
  }

  const columnas = [
    { clave: 'nombre_sucursal', encabezado: 'Nombre' },
    { clave: 'ubicacion_sucursal', encabezado: 'Ubicación' },
    { clave: 'telefono_sucursal', encabezado: 'Teléfono' },
    {
      clave: 'activo',
      encabezado: 'Estado',
      render: (fila) => (
        <span className={fila.activo ? styles.estadoActivo : styles.estadoInactivo}>
          {fila.activo ? 'Activa' : 'Inactiva'}
        </span>
      ),
    },
  ]

  return (
    <div className={styles.pagina}>
      <div className={styles.encabezado}>
        <h1 className={styles.titulo}>Sucursales</h1>
        {esAdmin && <BotonPrimario onClick={abrirCrear}>Nueva sucursal</BotonPrimario>}
      </div>

      {isLoading ? (
        <p>Cargando sucursales…</p>
      ) : (
        <Tabla
          columnas={columnas}
          datos={sucursales ?? []}
          mensajeVacio="Todavía no hay sucursales registradas."
          renderAcciones={
            esAdmin
              ? (fila) => (
                  <div className={styles.acciones}>
                    <button type="button" className={styles.enlaceAccion} onClick={() => abrirEditar(fila)}>
                      Editar
                    </button>
                    {fila.activo && (
                      <button
                        type="button"
                        className={styles.enlaceAccionPeligro}
                        onClick={() => setSucursalADesactivar(fila)}
                      >
                        Desactivar
                      </button>
                    )}
                  </div>
                )
              : undefined
          }
        />
      )}

      <Modal
        titulo={sucursalEnEdicion ? 'Editar sucursal' : 'Nueva sucursal'}
        abierto={formularioAbierto}
        onCerrar={cerrarFormulario}
      >
        <form className={styles.formulario} onSubmit={alGuardar} noValidate>
          <label className={styles.campo}>
            Nombre
            <input
              type="text"
              value={valores.nombre_sucursal}
              onChange={(evento) => setValores((v) => ({ ...v, nombre_sucursal: evento.target.value }))}
              required
            />
          </label>

          <label className={styles.campo}>
            Ubicación
            <input
              type="text"
              value={valores.ubicacion_sucursal}
              onChange={(evento) => setValores((v) => ({ ...v, ubicacion_sucursal: evento.target.value }))}
            />
          </label>

          <label className={styles.campo}>
            Teléfono
            <input
              type="text"
              value={valores.telefono_sucursal}
              onChange={(evento) => setValores((v) => ({ ...v, telefono_sucursal: evento.target.value }))}
            />
          </label>

          {errorFormulario && (
            <p className={styles.error} role="alert">
              {errorFormulario}
            </p>
          )}

          <div className={styles.accionesFormulario}>
            <BotonPrimario type="button" variante="secundario" onClick={cerrarFormulario}>
              Cancelar
            </BotonPrimario>
            <BotonPrimario type="submit" disabled={crear.isPending || editar.isPending}>
              {crear.isPending || editar.isPending ? 'Guardando…' : 'Guardar'}
            </BotonPrimario>
          </div>
        </form>
      </Modal>

      <Modal
        titulo="Desactivar sucursal"
        abierto={Boolean(sucursalADesactivar)}
        onCerrar={() => setSucursalADesactivar(null)}
      >
        <p className={styles.textoConfirmacion}>
          ¿Confirmas que quieres desactivar la sucursal "{sucursalADesactivar?.nombre_sucursal}"? Dejará de estar
          disponible para nuevos movimientos, pero su historial se conserva.
        </p>
        <div className={styles.accionesFormulario}>
          <BotonPrimario variante="secundario" onClick={() => setSucursalADesactivar(null)}>
            Cancelar
          </BotonPrimario>
          <BotonPrimario variante="peligro" onClick={confirmarDesactivar} disabled={desactivar.isPending}>
            {desactivar.isPending ? 'Desactivando…' : 'Desactivar'}
          </BotonPrimario>
        </div>
      </Modal>
    </div>
  )
}
