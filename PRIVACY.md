# Privacidad y consentimiento del cliente local

Esta herramienta funciona en el equipo de quien la ejecuta. El repositorio no
opera un servidor ni recibe tus datos o credenciales. Al utilizarla aceptas esta
información, las [condiciones de YouTube](https://www.youtube.com/t/terms) y las
condiciones de los demás servicios que hayas elegido. El programa solicita
aceptación explícita antes de enviar datos y confirmación final antes de subir.

## Datos y destinatarios

| Operación | Datos enviados | Destinatario |
| --- | --- | --- |
| `analyze` | Vídeo local, fuentes seleccionadas, instrucciones y clave para autenticar la petición | Gemini API / Google |
| OAuth | Solicitud de permisos y consentimiento mediante el navegador de Google | Google |
| Identificación del canal | Token OAuth; recibe ID y nombre del canal para mostrarlos | YouTube Data API |
| `upload` | Vídeo, título, descripción, etiquetas, idioma, privacidad y declaraciones infantiles/IA; token OAuth | YouTube |
| Aviso opcional | Identificador del chat, credencial del bot y mensaje genérico | Telegram Bot API |
| `revoke` | Token de esta aplicación que debe revocarse | Google OAuth |

No se envían contraseñas o cookies a este programa. No hay telemetría, publicidad,
consulta de estadísticas ni registro propio de errores o respuestas API. Los
proveedores reciben datos técnicos como la IP y aplican sus propias políticas.
Las URLs de fuentes deben ser públicas y no contener secretos, enlaces firmados
o información identificativa. Los ejemplos del repositorio no contienen datos reales.

No envíes datos personales, sensibles o confidenciales. Necesitas los derechos
necesarios para enviar el vídeo a Gemini y publicarlo en YouTube. Solo utiliza
Telegram con un bot y un chat autorizados. La disponibilidad regional, costes y
verificaciones dependen de los proveedores.

## Conservación local y control

- El cliente OAuth y el token se guardan fuera del repositorio en
  `$XDG_CONFIG_HOME/notebooklm-youtube-generator/` o, por defecto,
  `~/.config/notebooklm-youtube-generator/`.
- Los borradores se guardan en `$XDG_DATA_HOME/notebooklm-youtube-generator/` o
  `~/.local/share/notebooklm-youtube-generator/`, salvo que elijas otra ruta.
- Los archivos creados por la herramienta tienen permisos `0600`; sus carpetas
  predeterminadas tienen permisos `0700`. Esto no protege frente a un usuario
  con acceso a tu cuenta del sistema o a tus copias de seguridad.
- La herramienta no retiene historial de visualizaciones, IDs de vídeos o datos
  de otros usuarios. Los borradores, vídeos y fuentes permanecen en tu equipo
  hasta que decidas eliminarlos o exportarlos; no se borran automáticamente.
- Los metadatos y fuentes son JSON, y los vídeos son archivos locales: puedes
  exportarlos o eliminarlos directamente. Si decides dejar de usar la aplicación,
  revoca el acceso y elimina los archivos privados que ya no necesites.

El comando `revoke` intenta revocar inmediatamente la autorización OAuth en
Google y elimina el token local solo tras confirmar éxito. Alternativamente,
usa [las conexiones de tu cuenta](https://myaccount.google.com/connections).
Eliminar el token o un borrador local **no elimina vídeos ni datos en YouTube**.
Para modificar o eliminar un vídeo utiliza YouTube Studio. No hay publicación
programada: seleccionar `public` o `unlisted` hace efectiva esa visibilidad en
la subida; `private` es el valor predeterminado.

## Conservación en los proveedores

Cuando la subida devuelve un identificador, el programa intenta eliminar el
archivo de Gemini mediante Files API en un bloque de limpieza, también si el
análisis falla. Si la eliminación falla, el programa avisa. Si la subida falla
antes de devolver el identificador, no se puede confirmar si Gemini guardó el
archivo ni eliminarlo por su identificador: se avisa para que compruebes Files
API antes de reintentarlo. Una terminación forzada del proceso puede impedir
la limpieza y el aviso.

Comprueba tu cuenta y la [política de Files API](https://ai.google.dev/gemini-api/docs/files),
que actualmente indica la eliminación automática de archivos tras 48 horas.
Eliminarlo no garantiza eliminar registros de seguridad, respuestas ni todas
las copias que Google pueda conservar conforme a sus condiciones.

El tratamiento de datos en Gemini depende del país, la facturación y el
servicio utilizado. Puede incluir conservación para seguridad y, donde las
condiciones lo permitan, revisión humana o mejora de productos. No supongas
que toda API gratuita ni toda API de pago tienen el mismo tratamiento.

Al poner clientes Gemini API a disposición de usuarios del Espacio Económico
Europeo, Suiza o Reino Unido, las condiciones exigen servicios de pago; para
Gemini API, peticiones mediante un proyecto con facturación activa. Revisa la
aplicación de esta condición antes de distribuir u ofrecer el cliente en esas
regiones. Esta documentación y la publicación del código no certifican cumplimiento.

- [Gemini API: condiciones](https://ai.google.dev/gemini-api/terms)
- [Google: política de privacidad](https://policies.google.com/privacy)
- [Telegram: política de privacidad](https://telegram.org/privacy)

El cliente se distribuye como código local, no como un servicio gestionado para
terceros. Las cuestiones de configuración y borrado local pueden plantearse
al mantenedor mediante los Issues del repositorio donde obtuviste el código,
**sin adjuntar secretos, vídeos privados o tokens**. Las solicitudes relativas
a datos alojados en Google o Telegram deben dirigirse a esos proveedores.
Si despliegas este código para otros usuarios, publica tus propios datos de
contacto y adapta esta información a tu tratamiento real antes de ofrecerlo.
