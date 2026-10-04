# Revisión de la edición pública

Revisión inicial: 2 de octubre de 2026. Actualización: 4 de octubre de 2026.
Alcance: esta edición local, su contenido, objetos Git e índice; dependencias
fijadas en `requirements.txt`. No es una certificación de seguridad ni un
dictamen jurídico.

## Cambios de publicación

- Repositorio independiente, sin copiar el historial privado original.
- No se incluyen credenciales, perfiles, cookies, sesiones, registros, capturas,
  estadísticas personales, vídeos ni datos reales en los ejemplos.
- Se retiran la automatización de NotebookLM, ocultación de bots, grounding con
  Google Search, optimización basada en estadísticas y borrado automático.
- Subida mediante API oficial con revisión, edición de metadatos, identificación
  del canal, declaraciones explícitas y confirmación final. Privada por defecto,
  sin publicación programada.
- Archivos privados fuera del repositorio, permisos restringidos, comprobación
  de permisos al leer credenciales y protección frente a enlaces simbólicos.
- No se sobrescriben borradores. No se imprimen excepciones API privadas.
- Intento de limpieza del archivo remoto de Gemini cuando se conoce su
  identificador, incluso si falla el análisis; se avisa si la eliminación falla
  o si una subida incierta puede haber dejado un archivo remoto sin identificar.
- Revocación OAuth explícita y notificaciones Telegram sin metadatos ni errores.
- Lista de publicación cerrada, licencia MIT, documentación de privacidad y
  ejemplos ficticios sin claves de muestra reutilizables.
- Pruebas con directorios temporales estándar, sin depender de una carpeta
  propia de OpenCode; documentación del requisito regional de servicios de pago
  en Gemini para clientes puestos a disposición de usuarios del EEE, Suiza o Reino Unido.

## Comprobaciones

- 17 pruebas offline superadas para límites de metadatos, fuentes/URLs, permisos, lectura de
  archivos, cancelación previa y final, cuerpo exacto de subida, privacidad,
  conservación del vídeo, errores privados, OAuth, revocación y limpieza Gemini,
  incluidos fallos e interrupciones durante la subida y fallos de eliminación.
- Sintaxis Python, shell y JSON; ejecución de la ayuda CLI.
- Compatibilidad del esquema con el SDK instalado y de los campos con la
  documentación de descubrimiento de YouTube, sin solicitudes a cuentas reales.
- Auditoría de todos los archivos locales e índice, rutas históricas y todos
  los blobs Git locales, incluidos objetos no alcanzables.
- Detector independiente Gitleaks 8.30.1, con resultados redactados, aplicado
  al directorio, historial alcanzable y contenido de todos los blobs y commits
  locales, incluidos los no alcanzables: sin hallazgos.
- En la revisión inicial, comparación con 120 huellas de valores privados
  originales y variantes base64/hex: sin coincidencias. No se ha repetido en
  esta actualización; los valores no se publican en este informe.
- `pip check`: sin incompatibilidades en el entorno Linux/Python 3.12 probado.
- En la revisión inicial, `pip-audit` sobre las 38 dependencias de ejecución
  fijadas: sin vulnerabilidades conocidas. En esta actualización, consulta a
  OSV para las mismas versiones: sin avisos aplicables. Las herramientas de
  auditoría no se incluyen como dependencias del programa.
- Integridad Git comprobada mediante `git fsck --full`.

Repite las pruebas y `python3 audit_public.py` después de cualquier cambio.
Para una segunda comprobación independiente puedes instalar Gitleaks y ejecutar
`gitleaks dir . --redact=100` y `gitleaks git . --log-opts=--all --redact=100`.
Revisa las dependencias periódicamente: una consulta sin vulnerabilidades
conocidas no demuestra que no existan vulnerabilidades.

## Límites y acciones externas

El auditor incluido no analiza secretos en mensajes o metadatos de commits ni
tags; no se ha ampliado en esta actualización. El control independiente de
Gitleaks complementa ese límite, sin demostrar la ausencia de todo secreto.
La limpieza de Gemini es un intento, no una garantía: una subida incierta o una
terminación forzada puede dejar un archivo remoto, como explica `PRIVACY.md`.

No se han utilizado credenciales reales ni se han generado o subido vídeos.
La funcionalidad de servicios externos requiere una prueba consentida con una
cuenta propia y sigue sujeta a disponibilidad, costes, permisos y políticas.
No se ha publicado el repositorio ni configurado un remoto.

El original sigue siendo **privado y no publicable**, porque su historial se
conservó a petición de su propietario. Se eliminaron sus archivos privados de
ejecución del directorio de trabajo, no el historial ni copias externas.
No copies ni fusiones ese historial en esta edición.

Las sesiones o credenciales previamente compartidas deben revocarse en Google
y, si corresponde, regenerarse en Google Cloud y BotFather. Esta preparación
no invalida tokens o cookies en los servidores, ni elimina respaldos, forks o
copias de terceros. Tampoco garantiza derechos sobre tus fuentes, veracidad
de los vídeos, clasificación correcta o monetización.
