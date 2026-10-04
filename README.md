# Source to Screen

**AI-assisted video publishing with human review at every publishing boundary.**

Turn a video created in NotebookLM into a reviewed YouTube upload: draft metadata
with Gemini, edit it locally, authorize the destination channel, and publish
through the official YouTube Data API. Optional Telegram notifications close the
loop without sharing video details.

Python 3.11+ · Linux · [MIT license](LICENSE)

## Why this project

Preparing a video for publication involves more than generating its content.
Metadata needs editing, sources need attribution, the correct account needs
authorization, and visibility and content disclosures need deliberate choices.

Source to Screen automates the repeatable API work while keeping those editorial
decisions with the person publishing. It is a local, human-in-the-loop workflow,
not an unattended content-generation service.

| Capability | What it contributes |
| --- | --- |
| Multimodal metadata drafting | Gemini analyzes the actual video to propose a title, description, and tags. |
| Explicit publishing approval | The CLI shows the authorized channel and exact request before uploading. |
| Account-aware integration | OAuth handles access to YouTube; no browser passwords or session cookies are collected. |
| Conservative defaults | Uploads default to private, drafts are not overwritten, and source videos are never deleted. |
| Inspectable data | Sources and metadata are plain JSON that you can review, edit, export, or prepare manually. |
| Testable safety boundaries | Offline tests cover validation, consent, credentials, failure handling, and remote cleanup. |

The project demonstrates practical integration of asynchronous AI file processing,
OAuth, resumable media uploads, consent checkpoints, and publication auditing.
It does **not** independently verify facts, source licenses, or monetization eligibility.

## Workflow

```text
Select and review sources
          │
          ▼
NotebookLM: generate and download a Video Overview [manual]
          │
          ▼
Gemini API: analyze the local video and draft metadata [optional]
          │
          ▼
Watch the video, check facts and rights, edit the JSON [manual]
          │
          ▼
YouTube Data API: identify channel → review settings → confirm upload
          │
          ▼
Telegram Bot API: send a generic completion notice [optional]
```

**NotebookLM generation and download are manual.** This public edition does not
automate the NotebookLM website, use private APIs, scrape services, conceal bots,
or reuse Google Search grounding results. It does not collect YouTube statistics,
schedule publication, or delete videos or notebooks.

## Getting started

### Requirements

- Python **3.11 or later** on Linux. Credential-file protections use POSIX APIs;
  Windows is not supported by this implementation.
- A Google account and access to the services you choose to use. Gemini API
  users must be at least 18 years old.
- A Gemini API key for analysis, and/or your own Google Cloud OAuth client for
  YouTube uploads. Gemini analysis is optional.
- An MP4 or WebM video, no larger than **2 GiB**, and reviewed source information.
- Acceptance of [PRIVACY.md](PRIVACY.md) and the applicable provider terms.

### 1. Install

```bash
git clone https://github.com/macarronesc/notebooklm-youtube-generator.git
cd notebooklm-youtube-generator

python3 -m venv ~/.venvs/notebooklm-youtube-generator
source ~/.venvs/notebooklm-youtube-generator/bin/activate
python3 -m pip install -r requirements.txt
```

The runtime uses three Google SDKs. Their transitive dependencies are pinned in
`requirements.txt`; testing and security-audit tools are not runtime dependencies.

### 2. Configure Gemini

Create your own key in [Google AI Studio](https://aistudio.google.com/apikey).
Read it without putting the value into shell history or displaying it:

```bash
read -rs -p 'Gemini API key: ' GEMINI_API_KEY
export GEMINI_API_KEY
```

`.env.example` is a reference only: it contains empty credential fields and is
**not loaded automatically**. Do not put secrets in command arguments, source
files, screenshots, commits, or issue reports.

| Environment variable | Purpose | Default |
| --- | --- | --- |
| `GEMINI_API_KEY` | Authenticate video analysis | Required for `analyze` |
| `GEMINI_MODEL` | Select an available video-capable model | `gemini-flash-latest` |
| `TELEGRAM_BOT_TOKEN` | Authenticate optional notifications | Disabled unless both Telegram variables are set |
| `TELEGRAM_CHAT_ID` | Destination chat you control | No default |
| `XDG_CONFIG_HOME` | Base directory for local OAuth files | `~/.config` |
| `XDG_DATA_HOME` | Base directory for metadata drafts | `~/.local/share` |

Check model availability, pricing, and data handling in your region. API calls
can incur charges. When making Gemini API clients available to users in the
EEA, Switzerland, or the UK, the [Gemini terms](https://ai.google.dev/gemini-api/terms)
require Paid Services: API requests through a project with active billing.
Publishing source code does not configure billing or certify compliance.

### 3. Configure YouTube OAuth

1. Create your own project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **YouTube Data API v3** and configure the OAuth consent screen.
3. Create an OAuth client of type **Desktop app**, not a web client.
4. Download its configuration. Store it outside the repository at
   `~/.config/notebooklm-youtube-generator/client_secret.json`.
5. Restrict access to the directory and file:

```bash
mkdir -p ~/.config/notebooklm-youtube-generator
chmod 700 ~/.config/notebooklm-youtube-generator
chmod 600 ~/.config/notebooklm-youtube-generator/client_secret.json
```

If you set `XDG_CONFIG_HOME`, use that location instead. On first use, Google
opens the standard browser consent flow. The saved token has permissions `0600`.

| OAuth scope | Why it is requested |
| --- | --- |
| `youtube.upload` | Upload the video you approve. |
| `youtube.readonly` | Identify and display the authorized channel before uploading. No statistics are collected. |

OAuth verification and the YouTube API compliance audit are separate processes.
API projects subject to [YouTube's unverified-project restriction](https://developers.google.com/youtube/v3/docs/videos/insert)
can upload only in private mode. Do not attempt to bypass it. Publishing this
repository does not publish or verify your OAuth application.

## Usage

### Prepare sources and a video

Use NotebookLM to generate and download your video manually. Keep videos,
source manifests, drafts, and credentials **outside this repository**.

Copy [sources.example.json](examples/sources.example.json) to a private working
location, then replace its fictional entries with your reviewed sources. Each
entry needs `title`, `url`, `author`, and `license`. Use public URLs without
credentials, signed access links, or personal information.

The examples are format demonstrations, **not verified sources or valid permissions**.
Recording a license does not verify it, and attribution alone does not grant
permission. Add any required credits to the video description yourself; the
program does not append text after your approval.

### Draft metadata with Gemini

```bash
python3 youtube_pipeline.py analyze ~/Videos/video.mp4 \
  --sources ~/Documents/sources.json --language en
```

You must type `ACCEPT` before the video and source manifest are sent to Gemini.
The default draft location is:

```text
~/.local/share/notebooklm-youtube-generator/metadata.json
```

Drafts are written with permissions `0600` and never overwritten. For another
video, choose a new `--output` path. Watch the complete video, check its facts
and rights, and edit the JSON before proceeding.

Gemini file deletion is **best effort**. A failed upload may leave a remote file
without a returned identifier. Check the Files API before retrying; see
[data-retention limits](PRIVACY.md#provider-retention-and-cleanup).

### Review and upload

```bash
python3 youtube_pipeline.py upload ~/Videos/video.mp4 --language en
```

The CLI lets you edit the title and description, choose visibility, and explicitly
answer `y` or `n` for made-for-kids and synthetic-content declarations. It then
requests consent, identifies the authorized channel, and displays the exact API
request. The upload starts **only after you type `UPLOAD`**.

- **Private is the default.** Selecting `public` or `unlisted` requests that
  visibility immediately; there is no publication schedule.
- English is the default content language. Use `--language es` for Spanish in
  both commands. The CLI itself is in English.
- Use `--metadata /path/to/draft.json` to select a different draft.
- To skip Gemini entirely, prepare a draft using
  [metadata.example.json](examples/metadata.example.json) as the format reference.

### Revoke access

```bash
python3 youtube_pipeline.py revoke
```

The local token is deleted only after Google confirms revocation. You can also
revoke access through [your Google account connections](https://myaccount.google.com/connections).
This does not delete drafts or videos on YouTube.

### Optional Telegram notifications

Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` using hidden input, as for the
Gemini key. Use only a bot and chat you control and are authorized to contact.
The message is generic: no video title, URL, path, file, statistics, or API error
is sent. Notification failure does not delete or repeat the uploaded video.

## Safety and failure handling

- Credentials and drafts live outside the repository. Default application
  directories use `0700`; created private files use `0600`.
- Credential reads check ownership and permissions. JSON reads reject symlinks
  and oversized files; metadata validation rejects recognized secret patterns.
- Source URLs, title length, UTF-8 description size, tags, and content declarations
  are validated before publishing.
- Cancellation and failure return a nonzero exit status. Private exception
  messages and API responses are not printed.
- Local videos and notebooks are never automatically deleted.

These controls reduce risk; they do not prove that content is accurate, licensed,
safe, or compliant. Source files remain your responsibility, and provider data
handling follows their terms. Read [PRIVACY.md](PRIVACY.md) for the full data flow.

| Problem | What to check |
| --- | --- |
| Analysis fails | API key, model availability, billing, quotas, video format, source JSON, and whether the output path already exists. |
| Credential file is rejected | Desktop OAuth client type, file ownership, `0600` permissions, and the configured directory. |
| Upload fails or its outcome is uncertain | Check YouTube Studio before retrying. A network failure does not prove the server rejected the video. |
| Gemini cleanup cannot be confirmed | Inspect the Files API before retrying; do not assume the file was deleted. |
| Revocation fails | Use Google's account connections. Removing a local token alone does not revoke remote access. |

## Development and verification

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 audit_public.py
bash -n run.sh
```

Tests use mocked providers and do not access accounts or the network. The
publication auditor checks working files, JSON/Python syntax, the Git index,
historical paths, and **all local Git blobs, including unreachable objects**.
It reports categories and locations, never secret values.

The included auditor does not scan commit/tag messages or metadata. Complement
it with history review and an independent scanner such as Gitleaks:

```bash
gitleaks dir . --redact=100
gitleaks git . --log-opts=--all --redact=100
```

See [AUDIT.md](AUDIT.md) for dated findings and verification limits. A clean
pattern scan is not proof that every possible secret or vulnerability is absent.
Re-audit dependencies before updates and enable GitHub secret protection.

### Repository layout

```text
youtube_pipeline.py   Analysis, reviewed uploads, notifications, and revocation
audit_public.py       Offline publication checks and shared secret-pattern detection
tests/               Mocked safety and behavior checks
examples/            Fictional source and metadata JSON examples
run.sh               Thin CLI launcher
PRIVACY.md           Data recipients, retention, consent, and deletion
AUDIT.md             Dated review results and limitations
requirements.txt     Pinned runtime dependencies
```

Contributions should be focused, tested, and free of credentials or private
media. The `.gitignore` is a publication allowlist: deliberately review and allow
new files instead of forcing private files into Git. Do not post secrets in
issues; revoke exposed credentials and coordinate remediation without sharing
their values.

## Project history and scope

This edition derives from an earlier private prototype. Its public history was
reconstructed into technical milestones to make review easier. Commit dates
reflect preparation of the public edition, not the original private chronology.
Do not merge the original private history or copy its profiles, logs, tokens,
or backups into this repository.

This is a local integration project, not a hosted service or a compliance
certification. Offering it to other users requires appropriate consent, privacy,
security, verification, and deletion processes. Previously shared credentials
must be revoked with their providers; deleting local files does not invalidate
sessions or remove external copies.

Relevant provider policies:

- NotebookLM: [terms and rights](https://support.google.com/notebooklm/answer/17004255)
  and [Video Overview downloads](https://support.google.com/notebooklm/answer/16454555).
- Gemini: [API terms, regional requirements, and data handling](https://ai.google.dev/gemini-api/terms).
- YouTube: [terms](https://www.youtube.com/t/terms),
  [API policies](https://developers.google.com/youtube/terms/developer-policies),
  [minimum functionality](https://developers.google.com/youtube/terms/required-minimum-functionality),
  [synthetic content](https://support.google.com/youtube/answer/14328491),
  [made-for-kids content](https://support.google.com/youtube/answer/9528076),
  [spam](https://support.google.com/youtube/answer/2801973), and
  [monetization](https://support.google.com/youtube/answer/1311392).
- Telegram: [Bot Platform developer terms](https://telegram.org/tos/bot-developers).
- EU: [AI-generated content transparency](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act).

## License

The code is released under the [MIT license](LICENSE). This license does not
grant rights to third-party videos, source material, trademarks, or services.
Source to Screen is independent and is not affiliated with or endorsed by
Google, YouTube, or Telegram.
