import type { PeriodoAnterior, Variacion as ValorVariacion } from '../../../api/reportes'
import { AyudaInfo } from '../../../components/common/AyudaInfo'
import { describirPeriodoAnterior } from './formato'
import styles from './Variacion.module.css'

interface VariacionProps {
  // `undefined` mientras carga (no se pinta nada); `null` sin base de comparación.
  valor: ValorVariacion | undefined
  // Fechas del periodo anterior; si vienen, un icono de ayuda las muestra.
  periodoAnterior?: PeriodoAnterior
  // Para cifras donde subir no es bueno ni malo por sí mismo (gasto en compras).
  neutral?: boolean
  // Hacia dónde se abre la ayuda (indicadores alineados a la derecha: "derecha").
  alineacion?: 'izquierda' | 'derecha'
}

// Variación de un indicador contra el periodo anterior equivalente (016,
// "Actualización: periodos ampliados, comparación y producción"). El backend
// la calcula; aquí solo se muestra.
export function Variacion({ valor, periodoAnterior, neutral = false, alineacion = 'izquierda' }: VariacionProps) {
  if (valor === undefined) return null

  let texto = 'Sin datos del periodo anterior'
  let tono: 'neutro' | 'sube' | 'baja' = 'neutro'
  if (valor !== null) {
    const numero = Number(valor)
    const flecha = numero > 0 ? '▲' : numero < 0 ? '▼' : '='
    const porcentaje = Math.abs(numero).toLocaleString('es-MX', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
    texto = `${flecha} ${porcentaje} % vs. periodo anterior`
    tono = neutral || numero === 0 ? 'neutro' : numero > 0 ? 'sube' : 'baja'
  }
  const clases = { neutro: styles.variationNeutral, sube: styles.variationUp, baja: styles.variationDown }

  return (
    <span className={styles.variationRow}>
      <span className={`${styles.variation} ${clases[tono]}`} data-tono={tono}>
        {texto}
      </span>
      {periodoAnterior && (
        <AyudaInfo
          texto={describirPeriodoAnterior(periodoAnterior)}
          etiqueta="Con qué periodo se compara"
          alineacion={alineacion}
        />
      )}
    </span>
  )
}
