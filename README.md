# Sonrisas Colombia — editorial website

Sitio bilingüe estático, reconstruido para una presentación editorial premium. Inglés en `/`, español en `/es/`. No requiere npm, framework, base de datos ni servicios de terceros para funcionar.

## Ejecutar localmente

Requisitos: Python 3.10 o posterior.

```powershell
python src/build.py
python src/verify.py
python -m http.server 8765 --bind 127.0.0.1 --directory site
```

Abrir http://127.0.0.1:8765/es/ o http://127.0.0.1:8765/.

## Organización

- `src/content.json`: textos, tratamientos, preguntas y perfiles en ambos idiomas.
- `src/page.html`: plantilla semántica común.
- `src/build.py`: generador sin dependencias externas.
- `src/verify.py`: comprobaciones de integridad.
- `site/assets/style.css`: diseño responsive, fuentes locales y movimiento reducido.
- `site/assets/app.js`: menú, calculadora, diálogos, idioma y animación.
- `site/assets/config.js`: configuración pública generada; no guardar secretos.
- `site/assets/fonts`: Bodoni Moda y Manrope WOFF2 con licencias OFL.
- `site/assets/editorial-smile*`, `colombia*`: imágenes generadas, optimizadas en AVIF/WebP a dos tamaños.
- `work/`: respaldo de los archivos anteriores; ignorado por Git y Docker.

No se incluye lockfile npm porque no existe una instalación de paquetes JavaScript. La compilación utiliza exclusivamente la biblioteca estándar de Python. Se mantuvo una arquitectura estática para evitar dependencias innecesarias; no se requiere Astro para estas interacciones.

## Configurar

Las variables se leen durante la compilación. En PowerShell:

```powershell
$env:PUBLIC_WHATSAPP_NUMBER='NUMERO_REAL_SOLO_DIGITOS'
$env:PUBLIC_SITE_URL='https://DOMINIO_REAL'
python src/build.py
```

Sustituir esos valores antes de ejecutar. El generador no carga `.env` automáticamente en desarrollo local; Docker Compose sí lo utiliza para interpolar los argumentos. Copiar `.env.example` a `.env` para Compose.

- `PUBLIC_WHATSAPP_NUMBER`: número real internacional; sin espacios ni +. Sin configurar, los botones abren un diálogo informativo, no una reserva ficticia.
- `PUBLIC_SITE_URL`: origen HTTPS definitivo. Habilita canonical, hreflang, Open Graph con URL absoluta, sitemap y Organization JSON-LD sin credenciales inventadas.
- `ENABLE_INDEXING`: false por defecto. Requiere también dominio para producir index/follow y robots abierto.
- `PUBLIC_GA4_ID`, `PUBLIC_META_PIXEL_ID`, `PUBLIC_GTM_ID`: campos reservados de configuración.
- `ENABLE_GA4`, `ENABLE_META_PIXEL`, `ENABLE_GTM`: reservados, sin efecto. El código no carga etiquetas ni hace seguimiento, incluso si se completan los identificadores. Integrarlos requiere una implementación y revisión posterior.

Los valores de la calculadora no se guardan ni transmiten. Las preferencias de idioma y privacidad se guardan en localStorage cuando está disponible. No hay redirección automática de idioma: prevalece la ruta de la campaña o el enlace elegido.

## Coolify

1. Usar la raíz de este repositorio con Docker Compose y `docker-compose.yml`.
2. Configurar las variables públicas y asignar dominio al servicio `web`, puerto interno 80.
3. Compilar y desplegar. La imagen multi-stage genera el HTML antes de copiarlo a Nginx.
4. Validar `/`, `/es/`, `/health`, `/robots.txt` y, con dominio configurado, `/sitemap.xml`.

No se publican puertos del host, no hay redes externas obligatorias ni etiquetas manuales de Traefik. HTTPS y dominio los gestiona Coolify. Cambiar variables requiere reconstruir la imagen: Nginx no sustituye variables en tiempo de ejecución. Los archivos HTML generados también están disponibles en `site/` para alojamiento estático.

## Dirección visual y recursos

Portada fotográfica sobre ónix, serif editorial, marfil y dorado champán. Tratamientos en filas amplias, inversión en panel oscuro, perfiles tipográficos, recorrido vertical y fotografía de destino. Sin avisos visibles de prototipo.

Las imágenes se generaron con la herramienta integrada de generación de imágenes, no con un fotógrafo ni con pacientes reales:

- `editorial-smile`: retrato editorial de una mujer adulta anónima, sonrisa natural, fondo negro, luz cálida lateral, aretes dorados y composición de campaña de lujo; sin texto, instrumentos ni afirmación de resultado clínico.
- `colombia`: escena editorial inspirada en las calles históricas de Cartagena, arquitectura colonial, buganvilias y luz de atardecer; sin afirmar que sea la ubicación del consultorio.

No se utilizan estas imágenes como testimonios, retratos de las doctoras o casos antes/después. Los perfiles tienen monogramas. La galería clínica y el comparador antes/después se incorporarán con material autorizado, no con resultados fabricados.

Referencias de contenido consultadas: https://drajuliamolina.com/, https://www.omeristanbul.com/, https://cosmeticrestorativedentistry.com/, https://www.newteethnow.com/. Se tomaron como referencia la claridad de tratamientos, el recorrido internacional, las preguntas y la visibilidad del contacto, sin reutilizar afirmaciones ni materiales. La referencia dralejandroaristizabal.com no estuvo accesible mediante la herramienta de consulta.

## Pendientes antes de publicación

1. Número de WhatsApp y dominio definitivos.
2. Ciudad y dirección del consultorio, datos del responsable y canales de atención.
3. Fotografías y biografías verificadas de Vanessa Pulgarin y Katherine Peña.
4. Casos clínicos autorizados para galería y comparadores; reseñas verificadas si se desean.
5. Validación profesional del contenido clínico, costos, seguimiento y condiciones de consulta.
6. Política de privacidad completa y textos legales con datos del responsable. El diálogo actual describe el comportamiento técnico real, pero no sustituye esa documentación.
7. Revisión de políticas y consentimiento antes de integrar analítica o publicidad.
8. Prueba de despliegue en Coolify, Lighthouse y revisión de accesibilidad completa.

## Verificaciones ejecutadas

- Construcción de las dos rutas y comprobación de enlaces, anclas, imágenes, fuentes y paridad de traducciones.
- Sintaxis JavaScript con `node --check`.
- Navegador: 1440×1000, 768×1024 y 390×844 sin desbordamiento horizontal observado.
- Calculadora: 12000 frente a 4000+600+900+500 = 6000 de ahorro, 50%; 15000+600+900+500 = 5000 de costo adicional, 41.7%; origen cero bloqueado; reinicio comprobado.
- Móvil: 10000 frente a 3000+500+500+0 = 6000, 60%; menú abre y cierra al navegar.
- Cambio ES/EN, diálogos de contacto sin número y preferencias de privacidad comprobados.
- Todas las imágenes cargadas tras recorrer la página; no se observaron errores o advertencias de consola en la consulta realizada.
- Docker y Lighthouse no ejecutados: Docker no está disponible en el entorno. No se afirma conformidad WCAG ni puntuaciones de rendimiento.
