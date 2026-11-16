# Sonrisas Colombia

Sitio web de **www.sonrisascolombia.com**: diseño de sonrisa y ortodoncia invisible en Colombia para pacientes internacionales de Puerto Rico y New Jersey.

## Concepto

Dos odontólogas especialistas (diseño de sonrisa + ortodoncia invisible) que planifican cada caso juntas. El sitio **no ofrece paquetes de viaje**: el mensaje es "tu viaje lo organizas tú; tu tratamiento lo organizamos nosotras, cita por cita".

## Estructura

- `index.html` — página única con todas las secciones (hero, doctoras, tratamientos, proceso, valor, resultados, testimonios, FAQ, formulario).
- `assets/css/styles.css` — sistema de diseño: paleta "orquídea" (porcelana, grafito, ciruela, lila), tipografías Fraunces + Instrument Sans.
- `assets/js/i18n.js` — diccionario en inglés (el español vive en el HTML como idioma por defecto).
- `assets/js/main.js` — cambio de idioma ES/EN, menú móvil y formulario que abre WhatsApp con mensaje pre-llenado.

## Pendientes antes de lanzar

- [ ] Nombres reales y fotos de las dos doctoras (`index.html`, sección `#doctoras`).
- [ ] Número real de WhatsApp: reemplazar `570000000000` en `assets/js/main.js` (constante `WHATSAPP_NUMBER`), en el footer y en el botón flotante de `index.html`.
- [ ] Ciudad del consultorio (hoy el copy dice solo "Colombia").
- [ ] Fotos reales de casos antes/después (sección `#resultados`).
- [ ] Testimonios reales (los actuales son ilustrativos).
- [ ] Enlaces de Instagram/TikTok en el footer.
- [ ] Conectar el dominio www.sonrisascolombia.com (GitHub Pages u hosting elegido).
