import { useState } from 'react'

import logoFlebosil from '../../assets/flebosil_transparentbg/logo_flebosil_magentafont.png'
import type { ConsultaPeriodo, PeriodoDashboard } from '../../api/reportes'
import { formatearMoneda } from './compartido/formato'
import { SelectorPeriodo } from './compartido/SelectorPeriodo'
import { useSaldoCaja } from '../../hooks/useMovimientosCaja'
import { useValidarConsultaPeriodo } from '../../hooks/useResumenDashboard'
import { useUsuarioActual } from '../../hooks/useUsuarioActual'
import { SeccionClientes } from './secciones/SeccionClientes/SeccionClientes'
import { SeccionCompras } from './secciones/SeccionCompras/SeccionCompras'
import { SeccionFacturacion } from './secciones/SeccionFacturacion/SeccionFacturacion'
import { SeccionGanancias } from './secciones/SeccionGanancias/SeccionGanancias'
import { SeccionProduccion } from './secciones/SeccionProduccion/SeccionProduccion'
import { SeccionProductos } from './secciones/SeccionProductos/SeccionProductos'
import { SeccionVentas } from './secciones/SeccionVentas/SeccionVentas'
import styles from './Dashboard.module.css'

const PERIODOS_ADMIN: PeriodoDashboard[] = ['dia', 'semana', 'mes', 'año', 'personalizado']
// El operador solo consulta "Día": el backend responde 403 a cualquier otro
// periodo (016, "Actualización: periodos ampliados, comparación y
// producción"); aquí solo se omiten las demás pestañas.
const PERIODOS_OPERADOR: PeriodoDashboard[] = ['dia']

const MENSAJE_RANGO_INVALIDO = 'No se pudo aplicar el rango. Revisa las fechas e inténtalo de nuevo.'

// Primer mensaje de un error de DRF: `{"detail": "…"}` o `{"campo": ["…"]}`.
function mensajeDeError(err: unknown): string {
  const datos = (err as { response?: { data?: Record<string, unknown> } }).response?.data
  if (!datos) return MENSAJE_RANGO_INVALIDO
  const primero = Object.values(datos)[0]
  const mensaje = Array.isArray(primero) ? primero[0] : primero
  return typeof mensaje === 'string' ? mensaje : MENSAJE_RANGO_INVALIDO
}

function SaldoCajaAdmin() {
  const { data: saldos, isLoading } = useSaldoCaja()

  return (
    <div className={styles.cashBalance}>
      <span className={styles.cashBalanceLabel}>Saldo actual de la caja</span>
      <span className={styles.cashBalanceAmount}>
        {isLoading || !saldos ? '…' : formatearMoneda(saldos.saldo_actual)}
      </span>
    </div>
  )
}

export function Dashboard() {
  const [consulta, setConsulta] = useState<ConsultaPeriodo>({ periodo: 'dia' })
  const { data: usuario } = useUsuarioActual()
  const validarConsulta = useValidarConsultaPeriodo()
  const esAdmin = usuario?.rol === 'admin'

  // Se pide primero el resumen del rango: si el backend lo rechaza, se
  // muestra su mensaje y el panel conserva el periodo anterior.
  const aplicarRango = async (desde: string, hasta: string) => {
    const nueva: ConsultaPeriodo = { periodo: 'personalizado', desde, hasta }
    try {
      await validarConsulta(nueva)
    } catch (err) {
      return mensajeDeError(err)
    }
    setConsulta(nueva)
    return null
  }

  return (
    <div className="page">
      <header className={styles.hero}>
        <img src={logoFlebosil} alt="FleboSil" className={styles.dashboardLogo} />

        {esAdmin && <SaldoCajaAdmin />}

        <SelectorPeriodo
          periodos={esAdmin ? PERIODOS_ADMIN : PERIODOS_OPERADOR}
          consulta={consulta}
          onCambiar={setConsulta}
          onAplicarRango={aplicarRango}
        />

        {!esAdmin && <p className="pageHint">Cifras de tus propias ventas, compras y facturas.</p>}
      </header>

      {/* Ganancia y movimientos de caja: solo admin (el backend tampoco se los da al operador). */}
      {esAdmin && <SeccionGanancias consulta={consulta} />}
      <SeccionVentas consulta={consulta} />
      <SeccionCompras consulta={consulta} />
      <SeccionProduccion consulta={consulta} esAdmin={esAdmin} />
      <SeccionProductos consulta={consulta} esAdmin={esAdmin} />
      <SeccionClientes consulta={consulta} />
      <SeccionFacturacion consulta={consulta} />
    </div>
  )
}
