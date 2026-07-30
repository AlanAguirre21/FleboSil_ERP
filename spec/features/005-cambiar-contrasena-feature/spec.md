# 005 · Cambiar contraseña

**Estado:** propuesta

## Qué hace

Permite a un usuario establecer una nueva contraseña, únicamente tras haber validado correctamente su identidad en la feature `004 · Recuperar contraseña`. Solicita la nueva contraseña y su confirmación, valida que ambas coincidan y cumplan requisitos mínimos de seguridad, y al guardarla exitosamente inicia sesión automáticamente en el Dashboard principal.

## Por qué

Cierra el flujo de recuperación de acceso iniciado en la feature anterior — sin esta pantalla, verificar el código de recuperación no tendría ningún efecto útil para el usuario. Completar el flujo con inicio de sesión automático reduce fricción, evitando que el usuario tenga que volver a loguearse manualmente justo después de demostrar su identidad.

## Criterios de aceptación

- [ ] Esta pantalla solo es accesible tras una verificación de código exitosa desde `004 · Recuperar contraseña` — no es alcanzable navegando directo por URL sin ese contexto previo.
- [ ] El formulario solicita nueva contraseña y confirmación de nueva contraseña.
- [ ] Si ambas contraseñas no coinciden, se muestra un error claro antes de intentar guardar.
- [ ] La nueva contraseña debe cumplir requisitos mínimos de seguridad (longitud mínima, no ser idéntica a la anterior); si no los cumple, se informa específicamente cuál requisito falta.
- [ ] Al guardar exitosamente, la contraseña se almacena únicamente como hash, nunca en texto plano.
- [ ] Al completar el cambio, el usuario inicia sesión automáticamente y es redirigido al Dashboard principal.
- [ ] El código de recuperación usado para llegar a esta pantalla queda invalidado permanentemente tras el cambio exitoso, sin importar que aún esté dentro de su ventana de expiración.
- [ ] Si el contexto de verificación expira o es inválido (ej. el usuario llegó aquí sin pasar por el paso anterior), se redirige de vuelta a `004 · Recuperar contraseña` con un mensaje explicativo.

## Fuera de alcance

- No incluye la generación ni verificación del código de 6 dígitos — corresponde a `004 · Recuperar contraseña`.
- No incluye cambio de contraseña desde un usuario ya autenticado (ej. desde su perfil) — ese flujo, si se necesita, pertenece a `016 · Información de Usuario` como una feature o ajuste aparte, no a esta.
- No incluye políticas de expiración periódica obligatoria de contraseña (forzar cambio cada N días) — no contemplado para el volumen actual de usuarios.