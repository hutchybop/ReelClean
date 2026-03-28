"""Tests for execution path safety guards."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from reelclean.core.executor import execute_plan
from reelclean.core.models import (
    CleanupCandidate,
    CleanupKind,
    Decision,
    ProposalStatus,
    RenameProposal,
)


class ExecutorSafetyTests(unittest.TestCase):
    def test_blocks_rename_outside_safe_root(self) -> None:
        with tempfile.TemporaryDirectory() as root_tmp, tempfile.TemporaryDirectory() as out_tmp:
            root = Path(root_tmp)
            outside = Path(out_tmp)

            source = root / "Movie.2020.mkv"
            source.write_bytes(b"video")

            target = outside / "Bad" / "Bad.mkv"
            proposal = RenameProposal(
                movie_id="movie-1",
                source_movie_path=source,
                source_subtitle_paths=[],
                guessed_title="Movie",
                year_hint="2020",
                search_term="Movie",
                target_name="Bad",
                target_dir=target.parent,
                target_movie_path=target,
                target_subtitle_paths=[],
                tmdb_match=None,
                decision=Decision.ACCEPT,
                status=ProposalStatus.READY,
            )

            result = execute_plan(
                proposals=[proposal],
                cleanup_candidates=[],
                safe_root=root,
            )

            self.assertEqual(len(result.rename_operations), 1)
            self.assertEqual(result.rename_operations[0].status, "failed")
            self.assertIn("outside allowed root", result.rename_operations[0].message)

    def test_blocks_cleanup_outside_safe_root(self) -> None:
        with tempfile.TemporaryDirectory() as root_tmp, tempfile.TemporaryDirectory() as out_tmp:
            root = Path(root_tmp)
            outside = Path(out_tmp)

            rogue = outside / "rogue.nfo"
            rogue.write_text("bad", encoding="utf-8")

            candidate = CleanupCandidate(
                candidate_id="candidate-1",
                root_dir=root,
                path=rogue,
                relative_path="../rogue.nfo",
                kind=CleanupKind.NON_MEDIA_FILE,
                selected=True,
            )

            result = execute_plan(
                proposals=[],
                cleanup_candidates=[candidate],
                safe_root=root,
            )

            self.assertEqual(len(result.cleanup_operations), 1)
            self.assertEqual(result.cleanup_operations[0].status, "failed")
            self.assertTrue(rogue.exists())


if __name__ == "__main__":
    unittest.main()
