import { useId, useState } from 'react'

import {
  ETIQUETAS_MOTIVO_AJUSTE,
  type AjusteInventarioPayload,
  type MotivoAjusteInventario,
  type StockItem,
  type TipoItemInventario,
} from '../../api/inventario'
import { BotonPrimario } from '../../components/common/BotonPrimario'
import { Modal } from '../../components/common/Modal'
import { useAjustarInventario } from '../../hooks/useInventario'

// Ajuste manual de una fila de existencias (admin u operador; 011, "Actualización —
// ajuste de inventario…"): stock contado y/o stock mínimo, con un paso de
// confirmación antes de enviar. Mismo patrón de dos pasos que el traslado.

const PATRON_STOCK = /^\d+(\.\d{1,2})?$/
const PATRON_MINIMO = /^\d+$/

interface ModalAjusteInventarioProps {
  fila: StockItem
  tipo: TipoItemInventario
  sucursalId: number
  sucursalNombre: string
  onCerrar: () => void
}

function dosDecimales(valor: string | number): string {
  return Number(valor).toFixed(2)
}

// Signo de kárdex: "+3.00" entra, "−2.00" sale (signo menos tipográfico).
function conSigno(diferencia: number): string {
  return `${diferencia > 0 ? '+' : '−'}${Math.abs(diferencia).toFixed(2)}`
}

function textoDiferencia(diferencia: number): string {
  return `${conSigno(diferencia)} (${diferencia > 0 ? 'entrada' : 'salida'})`
}

function extraerMensajeError(err: unknown): string {
  const datos = (err as { response?: { data?: Record<string, unknown> } }).response?.data
  if (!datos) return 'No se pudo guardar el ajuste. Inténtalo de nuevo.'
  const primero = datos.detail ?? Object.values(datos)[0]
  const mensaje = Array.isArray(primero) ? primero[0] : primero
  return typeof mensaje === 'string' ? mensaje : 'No se pudo guardar el ajuste. Inténtalo de nuevo.'
}

export function ModalAjusteInventario({ fila, tipo, sucursalId, sucursalNombre, onCerrar }: ModalAjusteInventarioProps) {
  const ajustar = useAjustarInventario()
  const id = useId()
  const [paso, setPaso] = useState<'formulario' | 'confirmacion'>('formulario')
  const [stockActual, setStockActual] = useState(dosDecimales(fila.stock_actual))
  const [stockMinimo, setStockMinimo] = useState(String(Number(fila.stock_minimo)))
  const [motivo, setMotivo] = useState<MotivoAjusteInventario | ''>('')
  const [nota, setNota] = useState('')
  const [error, setError] = useState('')

  const stockValido = PATRON_STOCK.test(stockActual.trim())
  const minimoValido = PATRON_MINIMO.test(stockMinimo.trim())
  const diferencia = stockValido ? Number(stockActual) - Number(fila.stock_actual) : 0
  const cambiaStock = stockValido && diferencia !== 0
  const cambiaMinimo = minimoValido && Number(stockMinimo) !== Number(fila.stock_minimo)

  function validar(): string {
    if (!stockValido) return 'El stock actual debe ser un número mayor o igual a 0, con máximo 2 decimales.'
    if (!minimoValido) return 'El stock mínimo debe ser un número entero mayor o igual a 0.'
    if (cambiaStock && !motivo) return 'Elige el motivo del ajuste.'
    if (cambiaStock && motivo === 'otro' && !nota.trim()) return 'Describe el motivo del ajuste.'
    return ''
  }

  function irAConfirmacion() {
    const mensaje = validar()
    setError(mensaje)
    if (!mensaje) setPaso('confirmacion')
  }

  async function confirmar() {
    setError('')
    const datos: AjusteInventarioPayload = { tipo, sucursal: sucursalId, item_id: fila.id }
    if (cambiaStock && motivo) {
      Object.assign(datos, {
        stock_actual: stockActual.trim(),
        stock_actual_visto: fila.stock_actual,
        motivo_ajuste: motivo,
        nota: nota.trim(),
      })
    }
    if (cambiaMinimo) datos.stock_minimo = stockMinimo.trim()
    try {
      await ajustar.mutateAsync(datos)
      onCerrar()
    } catch (err) {
      setError(extraerMensajeError(err))
    }
  }

  return (
    <Modal titulo={paso === 'formulario' ? 'Ajustar inventario' : '¿Estás seguro?'} abierto onCerrar={onCerrar}>
      {paso === 'formulario' ? (
        <div className="form">
          <p className="confirmText">
            <strong>{fila.nombre}</strong> · {sucursalNombre}
          </p>

          <div className="formGrid">
            <div className="field">
              <label htmlFor={`${id}-stock`}>Stock actual</label>
              <input
                id={`${id}-stock`}
                type="number"
                min={0}
                step="0.01"
                inputMode="decimal"
                value={stockActual}
                onChange={(e) => setStockActual(e.target.value)}
                aria-describedby={`${id}-stock-ayuda`}
              />
              <span id={`${id}-stock-ayuda`} className="fieldHint">
                {cambiaStock
                  ? `${textoDiferencia(diferencia)} sobre ${dosDecimales(fila.stock_actual)}`
                  : `Registrado: ${dosDecimales(fila.stock_actual)}`}
              </span>
            </div>

            <div className="field">
              <label htmlFor={`${id}-minimo`}>Stock mínimo</label>
              <input
                id={`${id}-minimo`}
                type="number"
                min={0}
                step={1}
                inputMode="numeric"
                value={stockMinimo}
                onChange={(e) => setStockMinimo(e.target.value)}
                aria-describedby={`${id}-minimo-ayuda`}
              />
              <span id={`${id}-minimo-ayuda`} className="fieldHint">
                Al quedar por debajo, el ítem se marca como "Bajo mínimo".
              </span>
            </div>

            {cambiaStock && (
              <>
                <label className="field">
                  Motivo del ajuste
                  <select value={motivo} onChange={(e) => setMotivo(e.target.value as MotivoAjusteInventario | '')}>
                    <option value="">Selecciona…</option>
                    {Object.entries(ETIQUETAS_MOTIVO_AJUSTE).map(([valor, etiqueta]) => (
                      <option key={valor} value={valor}>
                        {etiqueta}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  {motivo === 'otro' ? 'Nota' : 'Nota (opcional)'}
                  <input type="text" maxLength={200} value={nota} onChange={(e) => setNota(e.target.value)} />
                </label>
              </>
            )}
          </div>

          {error && (
            <p className="errorMessage" role="alert">
              {error}
            </p>
          )}

          <div className="formActions">
            <BotonPrimario variante="secundario" onClick={onCerrar}>
              Cancelar
            </BotonPrimario>
            <BotonPrimario onClick={irAConfirmacion} disabled={!cambiaStock && !cambiaMinimo}>
              Guardar
            </BotonPrimario>
          </div>
        </div>
      ) : (
        <div className="form">
          <p className="confirmText">
            ¿Confirmas estos cambios en <strong>{fila.nombre}</strong> ({sucursalNombre})?
          </p>

          <ul className="confirmList">
            {cambiaStock && motivo && (
              <li>
                Stock actual: {dosDecimales(fila.stock_actual)} → <strong>{dosDecimales(stockActual)}</strong>
                {` (${conSigno(diferencia)}, ${ETIQUETAS_MOTIVO_AJUSTE[motivo]}${nota.trim() ? `: ${nota.trim()}` : ''})`}
              </li>
            )}
            {cambiaMinimo && (
              <li>
                Stock mínimo: {Number(fila.stock_minimo)} → <strong>{Number(stockMinimo)}</strong>
              </li>
            )}
          </ul>

          {cambiaStock && (
            <p className="fieldHint">El cambio de stock queda en el historial de movimientos como un ajuste.</p>
          )}

          {error && (
            <p className="errorMessage" role="alert">
              {error}
            </p>
          )}

          <div className="formActions">
            <BotonPrimario
              variante="secundario"
              onClick={() => {
                setError('')
                setPaso('formulario')
              }}
              disabled={ajustar.isPending}
            >
              Volver
            </BotonPrimario>
            <BotonPrimario onClick={confirmar} disabled={ajustar.isPending}>
              {ajustar.isPending ? 'Guardando…' : 'Confirmar'}
            </BotonPrimario>
          </div>
        </div>
      )}
    </Modal>
  )
}
