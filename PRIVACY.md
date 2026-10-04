# Privacy and consent for the local client

This tool runs on the operator's own computer. The repository does not operate
a server or receive your data or credentials. Using the tool requires acceptance
of this notice, [YouTube's terms](https://www.youtube.com/t/terms), and the terms
of any other services you choose to use. The CLI asks for explicit consent
before sending data and final confirmation before uploading to YouTube.

## Data and recipients

| Operation | Data sent | Recipient |
| --- | --- | --- |
| `analyze` | Local video, selected sources, instructions, and the key used to authenticate the request | Gemini API / Google |
| OAuth | Requested permissions and browser-based consent | Google |
| Channel identification | OAuth token; receives the channel ID and name for display | YouTube Data API |
| `upload` | Video, title, description, tags, language, visibility, made-for-kids and synthetic-content declarations; OAuth token | YouTube |
| Optional notification | Chat identifier, bot credential, and a generic completion message | Telegram Bot API |
| `revoke` | The application's token to be revoked | Google OAuth |

The tool does not collect browser passwords or cookies. It has no application
telemetry, advertising, statistics collection, or dedicated logs of API errors
and responses. Providers receive technical information such as your IP address
and apply their own policies. Source URLs must be public and contain no secrets,
signed access links, or identifying information. Repository examples are fictional.

Do not submit personal, sensitive, or confidential information. You need the
necessary rights to send the video to Gemini and publish it on YouTube. Use
Telegram only with an authorized bot and chat. Regional availability, charges,
and verification requirements depend on the providers.

## Local retention and control

- OAuth configuration and tokens are stored outside the repository under
  `$XDG_CONFIG_HOME/notebooklm-youtube-generator/`, defaulting to
  `~/.config/notebooklm-youtube-generator/`.
- Drafts are stored under `$XDG_DATA_HOME/notebooklm-youtube-generator/`,
  defaulting to `~/.local/share/notebooklm-youtube-generator/`, unless you select
  another output location.
- Files created by the tool have permissions `0600`; its default application
  directories have permissions `0700`. These controls do not protect against
  someone with access to your operating-system account or backups.
- The tool does not retain view-count histories, video IDs, or other users' data.
  Drafts, videos, and source manifests remain on your computer until you choose
  to delete or export them. They are not automatically removed.
- Metadata and sources are plain JSON, and videos remain local files. You can
  export or delete them directly. When you stop using the application, revoke
  its access and remove private files you no longer need.

The `revoke` command attempts to revoke the OAuth authorization immediately
with Google. It deletes the local token only after receiving confirmation of
success. Alternatively, use [your Google account connections](https://myaccount.google.com/connections).
Deleting a token or local draft **does not delete videos or data on YouTube**.
Use YouTube Studio to change or remove published content. No publication is
scheduled: selecting `public` or `unlisted` requests that visibility on upload;
`private` is the default.

## Provider retention and cleanup

When a Gemini upload returns a file identifier, the program attempts to delete
that file through the Files API in a cleanup block, including when analysis
fails. If deletion fails, it displays a warning. If an upload fails before
returning an identifier, the program cannot confirm whether Gemini stored the
file or delete it by identifier. It warns you to check the Files API before
retrying. Forcefully terminating the process can prevent cleanup and warnings.

Check your account and the [Files API documentation](https://ai.google.dev/gemini-api/docs/files),
which states that uploaded files are automatically deleted after 48 hours as
of the documented review. File deletion does not guarantee deletion of security
logs, responses, or every copy Google may retain under its terms.

Gemini data handling depends on your country, billing configuration, and the
service used. It can include retention for security and, where the terms permit,
human review or product improvement. Do not assume that all free services or
all paid services handle data in the same way.

When making Gemini API clients available to users in the EEA, Switzerland, or
the UK, the terms require Paid Services. For Gemini API, requests must use a
project with active billing. Review how this requirement applies before
distributing or offering the client in those regions. This notice and the
publication of source code do not certify compliance.

- [Gemini API terms](https://ai.google.dev/gemini-api/terms)
- [Google Privacy Policy](https://policies.google.com/privacy)
- [Telegram Privacy Policy](https://telegram.org/privacy)

## Questions and deployment for other users

This client is distributed as local source code, not a managed third-party
service. Questions about configuration or local deletion can be raised with
the maintainer through the repository's Issues, **without attaching secrets,
private videos, or tokens**. Requests concerning data hosted by Google or
Telegram must be directed to those providers.

If you deploy this code for other users, publish your own contact information
and adapt this notice to your actual data processing before offering the service.
