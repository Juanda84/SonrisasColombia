# Sonrisas Colombia — sitio web

Sitio estático y bilingüe para pacientes de Puerto Rico y Estados Unidos: español (es-PR) en `/` y en `/es/`, inglés en `/en/`. No usa npm, frameworks ni base de datos. Para generarlo basta con Python 3.10 o posterior.

## Ejecutar localmente

```powershell
python src/build.py
python src/verify.py
python -m http.server 8765 --bind 127.0.0.1 --directory site
```

Luego abre http://127.0.0.1:8765/ (español) o http://127.0.0.1:8765/en/ (inglés).

## Qué se edita y dónde

| Quiero cambiar… | Archivo |
|---|---|
| Precios (USD por diente) | `PRICES` en `src/build.py`: se reflejan en todo el sitio |
| Textos en español e inglés (portada) | `src/content.json` |
| Páginas por ciudad y guía de precios | `src/pages.json` |
| Estructura HTML de cada sección | funciones `render_*` en `src/build.py` y `src/page.html` |
| Estilos y animaciones | `site/assets/site.css` |
| Interacciones (WhatsApp, calculadora, ciudades, comparador) | `site/assets/site.js` |

**Contenido pendiente:** cualquier texto de `content.json` que empiece por `Aquí pones:` aparece en el sitio como un recuadro punteado que dice qué va ahí. Al reemplazarlo, el recuadro desaparece. La lista completa está en `PENDIENTES.md`.

## Secciones

1. Portada con precio "desde", comparador antes/después con barrido animado y las 4 ciudades.
2. Resultados: segundo comparador y espacios para casos reales y un video testimonial.
3. Tratamientos: resina, porcelana y ortodoncia, con precio, días de referencia y botón de WhatsApp que indica el tratamiento.
4. Calculadora "¿Cuánto te ahorras?": cotización estilo recibo que se envía por WhatsApp con material, cantidad, país y ciudad.
5. Qué incluye el plan.
6. Cómo funciona en 4 pasos, con la ruta de vuelo animada San Juan → ciudad elegida.
7. Ciudades: Bogotá, Medellín, Cali y Pereira. La ciudad elegida se agrega a todos los mensajes de WhatsApp.
8. Doctoras, opiniones, preguntas frecuentes y cierre con la guía de "3 fotos".

En móvil aparece una barra fija de WhatsApp. En escritorio, un botón flotante. Con `prefers-reduced-motion` se desactivan las animaciones.

## Páginas y SEO

Se generan 14 páginas (más `/es/`, copia de la portada en español):

| Español | Inglés |
|---|---|
| `/` | `/en/` |
| `/carillas-bogota/`, `/carillas-medellin/`, `/carillas-cali/`, `/carillas-pereira/`, `/carillas-armenia/` | `/en/veneers-bogota/`, `/en/veneers-medellin/`, `/en/veneers-cali/`, `/en/veneers-pereira/`, `/en/veneers-armenia/` |
| `/precio-carillas-colombia/` | `/en/veneers-colombia-cost/` |

Cada página tiene título y descripción propios, canonical, hreflang, Open Graph con `og-image.jpg` (1200×630) y datos estructurados en un `@graph`: `Dentist` con ofertas y precios, `WebSite`, `WebPage`, `FAQPage`, `BreadcrumbList` en las internas y `HowTo` (guía de 5 fotos) en la portada.

También se generan `sitemap.xml` (con hreflang), `robots.txt` (con permisos explícitos para buscadores de IA cuando la indexación está activa) y `llms.txt` (resumen del negocio para ChatGPT, Perplexity, Claude, etc.). La fecha de los precios está en `PRICES_UPDATED` (`src/build.py`).

## Configuración

Valores por defecto en `src/build.py` (se pueden cambiar con variables de entorno):

- `PUBLIC_SITE_URL`: `https://sonrisascolombia.com`. Genera canonical, hreflang, Open Graph, sitemap y datos estructurados (`Dentist`).
- `PUBLIC_WHATSAPP_NUMBER`: `573044650264`.
- `ENABLE_INDEXING`: `false`. Cámbialo a `true` cuando no queden contenidos pendientes, para que Google indexe el sitio.
- `PUBLIC_GA4_ID`, `PUBLIC_META_PIXEL_ID`, `PUBLIC_GTM_ID`: reservados. El código todavía no carga medición.

Todo el contenido se muestra siempre, con o sin dominio configurado.

## Caché

Cada referencia a `/assets/...` sale en el HTML con una huella de su contenido (`site.css?v=6ed7f7b64a`). Si un archivo cambia, cambia su URL y todos los navegadores, incluido Safari en iPhone, descargan la versión nueva. Nginx guarda esos archivos un año (`immutable`) y obliga a revisar siempre el HTML, `robots.txt`, `sitemap.xml`, `llms.txt` y `config.js` (`no-cache`). No hace falta borrar caché a mano después de publicar.

## Coolify

1. Usa la raíz del repositorio con Docker Compose (`docker-compose.yml`).
2. Asigna el dominio `sonrisascolombia.com` al servicio `web`, puerto interno 80.
3. Despliega. La imagen genera el HTML con Python y lo sirve con Nginx. Si cambias variables, debes reconstruir.
4. Valida `/`, `/en/`, `/health`, `/robots.txt` y `/sitemap.xml`.

## Imágenes

- `smile-example-*`: sonrisas sintéticas (generadas) para los comparadores. Reemplazarlas por casos reales autorizados.
- `studio-*`: fotografía editorial generada de materiales (resina, porcelana, alineador).
- `destination-medellin-*` y `destination-cocora-*`: Medellín y el Valle del Cocora (para Pereira), generadas.
- `destination-bogota-*` y `destination-cali-*`: fotos de Unsplash (licencia libre, uso comercial permitido). Bogotá: Random Institute. Cali, iglesia La Ermita: Juan Manuel Gonzalez Restrepo.
- `destination-pereira-*`: Pereira de noche con el viaducto (Wikimedia Commons, Norbey, CC BY-SA 4.0). Armenia usa `destination-cocora-*`.
- `place-*`: 20 fotos de sitios turísticos (4 por ciudad) de Wikimedia Commons con licencias CC0, CC BY o CC BY-SA. Autor, licencia y enlace de cada una están en `src/photo-credits.json` y se muestran debajo de cada foto, como piden esas licencias. Los textos de cada sitio están en `src/pages.json` (`cities.<ciudad>.places`).
- `xmas-*`: 15 fotos de Navidad de temporadas anteriores (3 por ciudad) para la sección «Navidad en…» de cada ciudad, de Wikimedia Commons y Flickr con licencias CC BY o CC BY-SA. Créditos en `src/photo-credits.json`; pies de foto en `src/pages.json` (`xmas.photos.<ciudad>`). Desaparecen solas con la sección después de `SEASON_END`.
- `katherine-*`: fotos reales de la Dra. Katherine Peña.
- `logo-transparent.webp`: el logo con fondo transparente, generado a partir de `logo-onix.webp`.
- Fuentes: Bodoni Moda y Manrope (licencia OFL) en `site/assets/fonts`.
