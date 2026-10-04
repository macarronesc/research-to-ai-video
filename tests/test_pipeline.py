"""Offline safety checks; no real credentials, account access or network requests."""

import copy
import io
import json
from pathlib import Path
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, Mock, patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audit_public
import youtube_pipeline as pipeline


class SafetyChecks(unittest.TestCase):
    def setUp(self):
        self.metadata = json.loads((Path(__file__).resolve().parents[1]
                                    / "examples/metadata.example.json").read_text())

    def test_metadata_boundaries(self):
        pipeline.validate_metadata(self.metadata)
        for field, values in {
            "title": ["", " ", "a" * 101, "bad<title", "line\nbreak", "escape\x1b"],
            "description": ["é" * 2501, "bad>description", "escape\x1b"],
            "tags": ["not a list", [""], [None], ["a" * 501], ["escape\x1b"]],
            "sources": [[], {}, [None]],
        }.items():
            for value in values:
                with self.subTest(field=field, value_type=type(value).__name__):
                    metadata = dict(self.metadata, **{field: value})
                    with self.assertRaises(ValueError):
                        pipeline.validate_metadata(metadata)
        self.metadata["title"] = "a" * 100
        self.metadata["description"] = "é" * 2500
        pipeline.validate_metadata(self.metadata)

    def test_sources_are_validated(self):
        for url in ["file:///etc/passwd", "https://user:password" + "@example.org", "javascript:alert(1)",
                    "https://example.org/ bad", "https://example.org/\n"]:
            source = dict(self.metadata["sources"][0], url=url)
            with self.subTest(url_scheme=url.split(":")[0]), self.assertRaises(ValueError):
                pipeline.validate_sources([source])

    def test_recognized_credentials_in_metadata_or_sources_are_rejected_before_display(self):
        fake = "AI" + "za" + "X" * 35
        metadata = dict(self.metadata, description=fake)
        with self.assertRaises(ValueError):
            pipeline.validate_metadata(metadata)
        source = dict(self.metadata["sources"][0], license=fake)
        with self.assertRaises(ValueError):
            pipeline.validate_sources([source])

    def test_explicit_flags_no_schedule_or_hidden_description_changes(self):
        before = copy.deepcopy(self.metadata)
        for visibility in ("private", "unlisted", "public"):
            for kids in (True, False):
                for synthetic in (True, False):
                    body = pipeline.upload_body(self.metadata, "es", visibility, kids, synthetic)
                    self.assertEqual(body["status"], {"privacyStatus": visibility,
                        "selfDeclaredMadeForKids": kids, "containsSyntheticMedia": synthetic})
                    self.assertEqual(body["snippet"]["description"], self.metadata["description"])
        self.assertEqual(before, self.metadata)
        for visibility, kids, synthetic in [("scheduled", False, False), ("private", None, False),
                                            ("private", False, "false")]:
            with self.assertRaises(ValueError):
                pipeline.upload_body(self.metadata, "es", visibility, kids, synthetic)

    def test_private_atomic_files_no_overwrite_and_no_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.json"
            pipeline.write_private_json(path, self.metadata)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(pipeline.read_json(path), self.metadata)
            self.assertEqual(pipeline.read_json(path, private=True), self.metadata)
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                pipeline.read_json(path, private=True)
            path.chmod(0o600)
            with self.assertRaises(FileExistsError):
                pipeline.write_private_json(path, {"changed": True})
            self.assertEqual(pipeline.read_json(path), self.metadata)
            link = path.parent / "link.json"
            link.symlink_to(path)
            with self.assertRaises(OSError):
                pipeline.read_json(link)
            with self.assertRaises(FileExistsError):
                pipeline.write_private_json(link, {"changed": True})
            self.assertEqual(list(path.parent.glob(".private-*")), [])
            oversized = path.parent / "oversized.json"
            oversized.write_text(" " * (1024 * 1024 + 1))
            with self.assertRaises(ValueError):
                pipeline.read_json(oversized)

    def test_analysis_cleans_up_remote_video_on_success_and_failure(self):
        args = SimpleNamespace(video="unused", sources="unused", output="unused", language="en")
        draft = {key: value for key, value in self.metadata.items() if key != "sources"}
        for failure in (None, "upload", "interrupted", "api", "json", "processing", "timeout", "cleanup"):
            client = MagicMock()
            remote = SimpleNamespace(name="files/example", state=SimpleNamespace(
                name="FAILED" if failure == "processing" else "PROCESSING" if failure == "timeout" else "ACTIVE"))
            client.files.upload.return_value = remote
            client.models.generate_content.return_value = SimpleNamespace(
                text="invalid json" if failure == "json" else json.dumps(draft))
            if failure in ("upload", "interrupted"):
                error = KeyboardInterrupt if failure == "interrupted" else RuntimeError
                client.files.upload.side_effect = error("private-response")
            if failure == "api":
                client.models.generate_content.side_effect = RuntimeError("private-response")
            if failure == "cleanup":
                client.files.delete.side_effect = RuntimeError("private-response")
            with self.subTest(failure=failure), \
                 patch.object(pipeline, "video_path", return_value=Path("unused.mp4")), \
                 patch.object(pipeline, "read_json", return_value=self.metadata["sources"]), \
                 patch.object(pipeline, "confirm"), \
                 patch.object(pipeline, "write_private_json") as write, \
                 patch.object(pipeline.Path, "exists", return_value=False), \
                 patch.object(pipeline.Path, "is_symlink", return_value=False), \
                 patch.dict("os.environ", {"GEMINI_API_KEY": "offline-example"}), \
                 patch("google.genai.Client") as factory, \
                 patch.object(pipeline.time, "monotonic", side_effect=[0, 601]), \
                 patch("sys.stdout", new=io.StringIO()), \
                 patch("sys.stderr", new=io.StringIO()) as output:
                factory.return_value.__enter__.return_value = client
                if failure not in (None, "cleanup"):
                    with self.assertRaises((ValueError, RuntimeError, TimeoutError, KeyboardInterrupt)):
                        pipeline.analyze(args)
                    write.assert_not_called()
                else:
                    pipeline.analyze(args)
                    self.assertEqual(write.call_args.args[1], self.metadata)
                if failure in ("upload", "interrupted"):
                    client.files.delete.assert_not_called()
                    self.assertIn("upload could not be confirmed", output.getvalue())
                else:
                    client.files.delete.assert_called_once_with(name="files/example")
                    if failure == "cleanup":
                        self.assertIn("could not be deleted", output.getvalue())
                    else:
                        self.assertEqual(output.getvalue(), "")
                self.assertNotIn("private-response", output.getvalue())

    def test_upload_success_uses_exact_reviewed_payload_and_preserves_video(self):
        args = SimpleNamespace(video="unused", metadata="unused", language="en")
        service = Mock()
        service.channels().list().execute.return_value = {"items": [
            {"id": "example-channel", "snippet": {"title": "Example"}}]}
        service.videos().insert().next_chunk.return_value = (None, {"id": "sample12345"})
        with patch.object(pipeline, "video_path", return_value=Path("unused.mp4")), \
             patch.object(pipeline, "read_json", return_value=self.metadata), \
             patch("builtins.input", side_effect=["Reviewed title", "Reviewed description", "", "n", "y", "ACCEPT", "UPLOAD"]), \
             patch.object(pipeline, "youtube_service", return_value=service), \
             patch("googleapiclient.http.MediaFileUpload"), \
             patch.object(pipeline, "notify_telegram") as notify, \
             patch.object(pipeline.Path, "unlink") as unlink, \
             patch("sys.stdout", new=io.StringIO()):
            pipeline.upload(args)
            body = service.videos().insert.call_args.kwargs["body"]
            self.assertEqual(body["snippet"]["title"], "Reviewed title")
            self.assertEqual(body["snippet"]["description"], "Reviewed description")
            self.assertEqual(body["status"]["privacyStatus"], "private")
            self.assertNotIn("publishAt", body["status"])
            unlink.assert_not_called()
            notify.assert_called_once_with()

    def test_revoke_deletes_token_only_after_remote_success(self):
        for failure in (False, True):
            with self.subTest(failure=failure), \
                 patch.object(pipeline.Path, "exists", return_value=True), \
                 patch.object(pipeline, "confirm"), \
                 patch.object(pipeline, "read_json", return_value={"token": "offline-example"}), \
                 patch.object(pipeline.Path, "unlink") as unlink, \
                 patch.object(pipeline, "urlopen") as network, \
                 patch("sys.stdout", new=io.StringIO()):
                network.return_value.__enter__.return_value.status = 200
                if failure:
                    network.side_effect = RuntimeError("private-response")
                    with self.assertRaises(RuntimeError):
                        pipeline.revoke(SimpleNamespace())
                    unlink.assert_not_called()
                else:
                    pipeline.revoke(SimpleNamespace())
                    unlink.assert_called_once_with()

    def test_oauth_checks_stored_scopes_and_refreshes_without_printing_secrets(self):
        for scenario in ("valid", "refresh", "missing-scopes", "refresh-failure"):
            credentials = Mock()
            credentials.has_scopes.return_value = scenario != "missing-scopes"
            credentials.valid = scenario not in ("refresh", "refresh-failure")
            credentials.refresh_token = "offline-example"
            credentials.to_json.return_value = "{}"
            if scenario == "refresh":
                credentials.refresh.side_effect = lambda _: setattr(credentials, "valid", True)
            if scenario == "refresh-failure":
                credentials.refresh.side_effect = RuntimeError("private-response")
            with self.subTest(scenario=scenario), \
                 patch.object(pipeline.Path, "exists", return_value=True), \
                 patch.object(pipeline, "read_json", return_value={}) as read, \
                 patch.object(pipeline, "write_private_json") as write, \
                 patch("google.oauth2.credentials.Credentials.from_authorized_user_info", return_value=credentials) as factory, \
                 patch("googleapiclient.discovery.build") as build:
                if scenario in ("missing-scopes", "refresh-failure"):
                    with self.assertRaises((ValueError, RuntimeError)):
                        pipeline.youtube_service()
                    write.assert_not_called()
                    build.assert_not_called()
                else:
                    pipeline.youtube_service()
                    write.assert_called_once()
                    build.assert_called_once()
                self.assertTrue(read.call_args.kwargs["private"])
                factory.assert_called_once_with({})

    def test_oauth_desktop_flow_and_rejection_of_web_client(self):
        for web_client in (False, True):
            secrets = {"web" if web_client else "installed": {}}
            credentials = Mock(valid=True)
            credentials.to_json.return_value = "{}"
            with self.subTest(web_client=web_client), \
                 patch.object(pipeline.Path, "exists", return_value=False), \
                 patch.object(pipeline, "read_json", return_value=secrets), \
                 patch.object(pipeline, "write_private_json") as write, \
                 patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_config") as factory, \
                 patch("googleapiclient.discovery.build") as build:
                factory.return_value.run_local_server.return_value = credentials
                if web_client:
                    with self.assertRaises(ValueError):
                        pipeline.youtube_service()
                    factory.assert_not_called()
                    write.assert_not_called()
                    build.assert_not_called()
                else:
                    pipeline.youtube_service()
                    factory.assert_called_once_with(secrets, pipeline.SCOPES)
                    arguments = factory.return_value.run_local_server.call_args.kwargs
                    self.assertEqual(arguments["authorization_prompt_message"], "")
                    self.assertEqual(arguments["timeout_seconds"], 600)
                    write.assert_called_once()

    def test_video_cannot_be_a_renamed_secret_or_a_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "video.mp4"
            path.write_bytes(b"not a video")
            with self.assertRaises(ValueError):
                pipeline.video_path(path)
            path.write_bytes(b"\x00\x00\x00\x18ftypisom")
            self.assertEqual(pipeline.video_path(path), path)
            link = path.parent / "link.mp4"
            link.symlink_to(path)
            with self.assertRaises(ValueError):
                pipeline.video_path(link)

    def test_cancellation_prevents_authentication_and_upload(self):
        args = SimpleNamespace(video="unused", metadata="unused", language="es")
        with patch.object(pipeline, "video_path", return_value=Path("unused.mp4")), \
             patch.object(pipeline, "read_json", return_value=self.metadata), \
             patch("builtins.input", side_effect=["", "", "", "n", "y", "NO"]), \
             patch.object(pipeline, "youtube_service") as service, \
             patch("sys.stdout", new=io.StringIO()):
            with self.assertRaises(ValueError):
                pipeline.upload(args)
            service.assert_not_called()

    def test_final_confirmation_prevents_upload_even_after_authentication(self):
        args = SimpleNamespace(video="unused", metadata="unused", language="es")
        service = Mock()
        service.channels().list().execute.return_value = {"items": [
            {"id": "example-channel", "snippet": {"title": "Example channel"}}]}
        with patch.object(pipeline, "video_path", return_value=Path("unused.mp4")), \
             patch.object(pipeline, "read_json", return_value=self.metadata), \
             patch("builtins.input", side_effect=["", "", "", "n", "y", "ACCEPT", "NO"]), \
             patch.object(pipeline, "youtube_service", return_value=service), \
             patch("sys.stdout", new=io.StringIO()):
            with self.assertRaises(ValueError):
                pipeline.upload(args)
            service.videos.assert_not_called()

    def test_missing_boolean_answer_is_not_false(self):
        for answer in ("", "yes", "false", "s"):
            with patch("builtins.input", return_value=answer), self.assertRaises(ValueError):
                pipeline.choose_boolean("Example")

    def test_english_confirmations_remain_explicit(self):
        with patch("builtins.input", return_value="ACCEPT") as prompt:
            pipeline.confirm("Example consent")
            self.assertIn("Type ACCEPT", prompt.call_args.args[0])
        for answer in ("", "accept", "yes", "NO"):
            with patch("builtins.input", return_value=answer), self.assertRaises(ValueError):
                pipeline.confirm("Example consent")
        for answer, expected in (("y", True), ("Y", True), ("n", False)):
            with patch("builtins.input", return_value=answer) as prompt:
                self.assertEqual(pipeline.choose_boolean("Example declaration"), expected)
                self.assertIn("y/n, no default", prompt.call_args.args[0])

    def test_cli_defaults_to_english_and_keeps_spanish_available(self):
        for command in ("analyze", "upload"):
            for language in (None, "es"):
                arguments = ["youtube_pipeline.py", command, "unused.mp4"]
                if command == "analyze":
                    arguments += ["--sources", "unused.json"]
                if language:
                    arguments += ["--language", language]
                with self.subTest(command=command, language=language), \
                     patch("sys.argv", arguments), patch.object(pipeline, command) as operation:
                    self.assertEqual(pipeline.main(), 0)
                    self.assertEqual(operation.call_args.args[0].language, language or "en")

    def test_cli_errors_do_not_print_private_exception_content(self):
        secret = "private-" + "exception-content"
        with patch.object(pipeline, "video_path", side_effect=RuntimeError(secret)), \
             patch("sys.argv", ["youtube_pipeline.py", "upload", "unused.mp4"]), \
             patch("sys.stderr", new=io.StringIO()) as output:
            self.assertEqual(pipeline.main(), 1)
            self.assertNotIn(secret, output.getvalue())

    def test_notification_contains_no_video_data_and_hides_errors(self):
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "example", "TELEGRAM_CHAT_ID": "example"}), \
             patch.object(pipeline, "urlopen", side_effect=RuntimeError("private-response")) as network, \
             patch("sys.stderr", new=io.StringIO()) as output:
            pipeline.notify_telegram()
            self.assertNotIn("private-response", output.getvalue())
            payload = network.call_args.args[0].data.decode()
            self.assertNotIn("youtube.com", payload)
            self.assertNotIn("metadata", payload)

    def test_auditor_detects_secret_patterns_without_real_secrets(self):
        fake = ("AI" + "za" + "X" * 35).encode()
        self.assertIn("Google API credential", audit_public.findings(fake))
        self.assertEqual(audit_public.findings(b"GEMINI_API_KEY=\n"), [])


if __name__ == "__main__":
    unittest.main()
