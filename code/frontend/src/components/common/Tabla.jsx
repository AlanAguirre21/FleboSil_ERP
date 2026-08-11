import styles from './Tabla.module.css'

export function Tabla({ columnas, datos, claveFila = 'id', renderAcciones, mensajeVacio = 'Sin datos para mostrar.' }) {
  return (
    <div className={styles.contenedor}>
      <table className={styles.tabla}>
        <thead>
          <tr>
            {columnas.map((columna) => (
              <th key={columna.clave}>{columna.encabezado}</th>
            ))}
            {renderAcciones && <th>Acciones</th>}
          </tr>
        </thead>
        <tbody>
          {datos.map((fila) => (
            <tr key={fila[claveFila]}>
              {columnas.map((columna) => (
                <td key={columna.clave}>{columna.render ? columna.render(fila) : fila[columna.clave]}</td>
              ))}
              {renderAcciones && <td>{renderAcciones(fila)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
      {datos.length === 0 && <p className={styles.vacio}>{mensajeVacio}</p>}
    </div>
  )
}
