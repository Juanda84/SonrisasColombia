# Material pendiente para sonrisascolombia.com

En el sitio, cada recuadro punteado con la etiqueta **"Contenido pendiente"** empieza por **"Aquí pones:"** y dice qué va en ese lugar. Todos los textos están en `src/content.json` (español en `es`, inglés en `en`). Al reemplazar un texto que empieza por "Aquí pones:", el recuadro desaparece solo y se muestra el contenido normal.

## 1. Precios (lo más urgente)

Están en **un solo lugar**: `PRICES` en `src/build.py` (USD por diente). Se actualizan solos en portada, tratamientos, calculadora, tabla comparativa y preguntas frecuentes.

| Dato | Valor de referencia actual | Fuente aproximada (nov. 2026) |
|---|---|---|
| Resina en Colombia | USD 180 | Rango de mercado USD 120–400 |
| Porcelana en Colombia | USD 420 | Rango de mercado USD 300–650 |
| Resina en Puerto Rico | USD 400 | Estimado (no hay buen dato público) |
| Porcelana en Puerto Rico | USD 750 | Rango USD 600–900 |
| Resina en EE. UU. | USD 800 | Promedio nacional |
| Porcelana en EE. UU. | USD 1.450 | Promedio nacional |
| Ortodoncia "desde" | — | `treatments[2].price` en `content.json` |

Confirma también los días de referencia en Colombia (hoy: resina 3–5 días, porcelana 7–10 días).

## 2. Fotos

| Dónde | Qué necesitas | Formato sugerido |
|---|---|---|
| Resultados | Foto real ANTES de un paciente, con autorización firmada | Horizontal 4:3, 1600×1200, mismo encuadre que el DESPUÉS |
| Resultados | Foto real DESPUÉS del mismo paciente, misma luz y ángulo | Horizontal 4:3, 1600×1200 |
| Ciudades (opcional) | Fotos reales de las 4 sedes (hoy se ven fotos de cada ciudad) | Horizontal, 1600×1000 |
| Doctoras | Foto profesional de la Dra. Vanessa Pulgarin, mismo estilo que las de Katherine | Vertical 3:4, 1200×1600 |

- Navidad en Armenia: no hay fotos libres del alumbrado de Armenia. Por ahora se muestran fotos del Quindío (faroles de Quimbaya, la plaza de Salento y faroles de la Noche de Velitas). Si tienes fotos propias del alumbrado de Armenia, cámbialas por `site/assets/xmas-armenia-*`.

## 3. Video

| Dónde | Qué necesitas | Formato |
|---|---|---|
| Resultados | Testimonio de un paciente real contando su experiencia (con autorización) | Vertical 9:16, 15–30 s, con subtítulos |
| Opcional, para la portada | Video corto del proceso: diseño digital, prueba y entrega | Horizontal o vertical, 10–20 s, sin audio |

## 4. Textos y datos

- **Direcciones de las 4 sedes** (Bogotá, Medellín, Cali, Pereira).
- **Credenciales de cada doctora:** universidad, especialización, años de experiencia y número de registro ReTHUS.
- **3 reseñas reales** (idealmente de Google): texto, nombre o iniciales y ciudad. Y la calificación promedio con el enlace al perfil.
- **¿Ofrecen traslado desde el aeropuerto?** Sí o no, y en qué ciudades.
- **Garantía** de las carillas (años en porcelana y en resina).
- **Formas de pago** (tarjeta, transferencia, financiación).
- **Datos legales:** razón social, NIT y dirección del responsable (pie de página).
- **Política de tratamiento de datos** completa (enlace en el aviso de privacidad).

## 5. Revisar antes de anunciar

- "Te respondemos con un estimado": confirma que el equipo puede contestar rápido por WhatsApp.
- "Vuelos desde San Juan" (Bogotá): verifica las rutas vigentes antes de pautar.
- Cuando no queden recuadros pendientes, activa la indexación en Google con `ENABLE_INDEXING=true`.

## 6. SEO, GEO y AEO (fuera del código)

- **Activar la indexación:** `ENABLE_INDEXING=true` en Coolify cuando el contenido esté listo. Hasta entonces Google y las IAs no ven el sitio.
- **Google Business Profile:** un perfil por sede (Bogotá, Medellín, Cali, Pereira) con dirección, horario, fotos y el enlace a su página (`/carillas-<ciudad>/`).
- **Google Search Console:** verificar el dominio y enviar `https://sonrisascolombia.com/sitemap.xml`.
- **Reseñas reales** en Google de pacientes de Puerto Rico y EE. UU.; luego llevarlas al sitio.
- **Redes sociales:** cuando existan, agregar sus enlaces en `sameAs` (datos estructurados) para que Google y las IAs conecten la marca.
- **Credenciales de las doctoras** (ReTHUS, universidad): al tenerlas, se agregan a la página y a los datos estructurados de cada doctora.
