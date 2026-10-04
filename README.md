# NotebookLM → Gemini → YouTube: flujo editorial revisado

Proyecto de portfolio que integra análisis audiovisual con Gemini, OAuth y
subidas mediante YouTube Data API. Admite contenido en español e inglés y
notificaciones opcionales por Telegram. No es un producto oficial de Google.

## Historial de esta edición

Esta edición deriva de un prototipo privado anterior. Para facilitar su revisión,
el historial público se ha reconstruido por etapas técnicas a partir de la
versión saneada. Las fechas son reales y corresponden a esta preparación; no
representan la cronología original del desarrollo privado.

## Flujo y límites

1. Elige un tema y revisa fuentes y permisos.
2. Genera el Video Overview **manualmente** en NotebookLM y descarga el vídeo.
3. La API de Gemini prepara un borrador de metadatos, con tu autorización.
4. Revisa el vídeo completo, contrasta los hechos y edita los metadatos.
5. El programa muestra el canal y los datos exactos; solo sube tras confirmar.

La versión histórica automatizaba la web. Esta versión pública **no incluye
Playwright, cookies, perfiles, ocultación de automatización, scraping, APIs
privadas ni reutilización de resultados de Google Search grounding**. No se
programan publicaciones, no se borran vídeos/notebooks y no se recopilan
estadísticas de YouTube. La privacidad predeterminada es `private`.

La herramienta no verifica automáticamente hechos, licencias ni la idoneidad
para monetización. Usar IA o citar una fuente no concede derechos sobre ella.
No envíes datos personales, credenciales o información confidencial a los servicios.

## Instalación

Requiere Python 3.11+ en Linux, una cuenta adulta de Google y acceso a las APIs.
Revisa y acepta [la información de privacidad](PRIVACY.md) antes de utilizarlo.

```bash
python3 -m venv ~/.venvs/notebooklm-youtube-generator
source ~/.venvs/notebooklm-youtube-generator/bin/activate
pip install -r requirements.txt
```

### Gemini

Obtén tu propia clave en [Google AI Studio](https://aistudio.google.com/apikey).
No la escribas en código, ejemplos, commits, capturas o argumentos de comandos.
Este ejemplo solicita el secreto sin incluirlo en el historial de la shell:

```bash
read -rs -p 'Gemini API key: ' GEMINI_API_KEY
export GEMINI_API_KEY
```

`.env.example` es solo una referencia con campos vacíos; **no se carga**.
`GEMINI_MODEL` permite elegir un modelo disponible; su valor predeterminado es
`gemini-flash-latest`. Comprueba disponibilidad, precios y tratamiento de datos
en tu región. Las operaciones pueden generar costes.

Al poner un cliente Gemini API a disposición de usuarios del Espacio Económico
Europeo, Suiza o Reino Unido, sus [condiciones](https://ai.google.dev/gemini-api/terms)
exigen utilizar servicios de pago: un proyecto con facturación activa para las
peticiones API. Revisa cómo se aplica esta condición a tu distribución; publicar
código no certifica su cumplimiento ni configura la facturación.

### YouTube OAuth

1. Crea tu propio proyecto en [Google Cloud Console](https://console.cloud.google.com/).
2. Habilita YouTube Data API v3 y configura correctamente el consentimiento OAuth.
3. Crea un cliente OAuth de tipo **Desktop app**, no de tipo web.
4. Guarda el JSON descargado como
   `~/.config/notebooklm-youtube-generator/client_secret.json`.
5. Protege la carpeta y el archivo:

```bash
mkdir -p ~/.config/notebooklm-youtube-generator
chmod 700 ~/.config/notebooklm-youtube-generator
chmod 600 ~/.config/notebooklm-youtube-generator/client_secret.json
```

El navegador realiza el consentimiento OAuth normal. No se guardan contraseñas
ni cookies del navegador. Los permisos son `youtube.upload` para subir y
`youtube.readonly` para identificar el canal autorizado; no se almacenan sus
estadísticas. El token local se guarda con permisos `0600`, fuera del repositorio.

La verificación OAuth, sus excepciones para uso personal y la auditoría de
YouTube son procesos distintos. Los proyectos API no verificados sujetos a la
restricción de YouTube pueden subir únicamente en privado. No intentes eludirla.
Hacer público este repositorio no equivale a publicar una aplicación OAuth.

## Uso

Guarda los vídeos, fuentes y borradores **fuera de este repositorio**. Los ejemplos
de `examples/` son ficticios: no son fuentes verificadas ni permisos válidos.
Cada fuente debe indicar `title`, `url`, `author` y `license`; verifica tú mismo
sus derechos y evita enlaces privados o firmados. Las atribuciones exigidas
deben añadirse a la descripción: el programa no modifica el texto después de
tu confirmación.

```bash
python3 youtube_pipeline.py analyze ~/Videos/video.mp4 \
  --sources ~/Documents/fuentes.json --language es
```

La eliminación del archivo remoto de Gemini se intenta, no se garantiza. Si
la subida no puede confirmarse, puede haber un archivo remoto sin eliminar:
comprueba Files API antes de reintentarlo. Consulta los límites en [PRIVACY.md](PRIVACY.md).

El borrador se guarda por defecto en
`~/.local/share/notebooklm-youtube-generator/metadata.json`, con permisos `0600`.
No se sobrescriben borradores existentes: usa `--output` con otra ruta para
vídeos posteriores. Edita el JSON y verifica el vídeo antes de continuar:

```bash
python3 youtube_pipeline.py upload ~/Videos/video.mp4 --language es
```

Puedes usar `--metadata` para seleccionar otro borrador y `--language en` para
inglés. También puedes preparar metadatos manualmente, sin enviar nada a Gemini,
siguiendo la estructura de `examples/metadata.example.json`.

Durante la subida puedes modificar título, descripción y privacidad. Debes
declarar explícitamente si el vídeo está creado para niños y si requiere aviso
de contenido sintético. La confirmación final muestra el canal y el cuerpo
exacto de la petición. Los fallos o cancelaciones devuelven un estado no cero;
no se imprimen excepciones ni respuestas API privadas y no se elimina tu vídeo.
Si una subida falla, comprueba YouTube Studio antes de volver a intentarlo:
un error de red no prueba que el servidor no recibiera el archivo.

Para revocar el acceso de esta aplicación:

```bash
python3 youtube_pipeline.py revoke
```

También puedes revocarlo en [las conexiones de tu cuenta de Google](https://myaccount.google.com/connections).
Si falla la revocación remota, el token local no se borra silenciosamente.

### Telegram opcional

Configura `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` mediante variables de entorno,
usando entrada oculta como para Gemini, y solo con un bot/chat que controles.
Solo se envía un aviso genérico de subida completada: ningún título, URL del
vídeo, ruta, archivo, estadística o error. No se realizan envíos masivos.

## Verificación antes de publicar

Consulta el alcance y los resultados en [AUDIT.md](AUDIT.md).

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 audit_public.py
bash -n run.sh
```

Las pruebas no utilizan cuentas ni la red. La auditoría busca formatos comunes
de secretos en los archivos locales y **todos los blobs Git locales, incluidos
los no alcanzables**; comprueba también el índice y las rutas históricas contra
la lista de publicación. No analiza secretos en mensajes o metadatos de commits
ni tags: complementa este control con revisión del historial y Gitleaks.
Falla si hay vídeos, perfiles, `.env` reales u otros archivos no permitidos.
No imprime los secretos detectados.

La `.gitignore` utiliza una lista explícita de archivos permitidos. Antes de
añadir otro archivo, revisa su contenido y autorízalo deliberadamente. No uses
`git add -f` para introducir datos privados. Una auditoría por patrones no es
una prueba matemática de ausencia de secretos; revisa también el diff y los
archivos que subes, y activa la protección de secretos de GitHub.

Este repositorio limpio no debe fusionarse con el historial privado original.
No copies perfiles, `.git`, registros, tokens ni respaldos de ese repositorio.
Las sesiones o credenciales ya compartidas deben revocarse en sus servicios:
eliminar un archivo local no las invalida ni borra copias externas.

## Políticas y responsabilidad

La versión está diseñada para reducir riesgos, no para certificar legalidad,
cumplimiento absoluto o seguridad futura. Revisa las políticas vigentes y tus
fuentes antes de utilizar o distribuir un cliente. Si ofreces un servicio a
terceros, necesitas adaptar consentimiento, privacidad, seguridad, verificación
y mecanismos de eliminación; esta herramienta es local, no un SaaS.

- [NotebookLM: términos y derechos](https://support.google.com/notebooklm/answer/17004255)
- [NotebookLM: descarga de Video Overviews](https://support.google.com/notebooklm/answer/16454555)
- [Gemini API: condiciones y tratamiento de datos](https://ai.google.dev/gemini-api/terms)
- [YouTube: términos](https://www.youtube.com/t/terms),
  [políticas API](https://developers.google.com/youtube/terms/developer-policies) y
  [funcionalidad mínima](https://developers.google.com/youtube/terms/required-minimum-functionality)
- [YouTube: restricción de proyectos no verificados](https://developers.google.com/youtube/v3/docs/videos/insert)
- [YouTube: contenido sintético](https://support.google.com/youtube/answer/14328491),
  [contenido infantil](https://support.google.com/youtube/answer/9528076),
  [spam](https://support.google.com/youtube/answer/2801973) y
  [monetización](https://support.google.com/youtube/answer/1311392)
- [Telegram: condiciones para desarrolladores](https://telegram.org/tos/bot-developers)
- [UE: transparencia de contenido generado con IA](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act)

Código bajo [licencia MIT](LICENSE). Esta licencia no cubre tus vídeos, fuentes,
marcas ni servicios de terceros. Proyecto independiente, sin afiliación ni
respaldo de Google, YouTube o Telegram.
