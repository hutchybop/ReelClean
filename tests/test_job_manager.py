"""Tests for web job manager workflows."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from reelclean.core.models import Decision, TmdbMatch
from reelclean.web.job_manager import JobManager, MODE_RENAME_ONLY


class FakeTMDB:
    """Simple TMDB stub for deterministic workflow tests."""

    def lookup(self, title: str, year_hint: str | None = None) -> TmdbMatch | None:
        if "movie" in title.lower():
            return TmdbMatch(
                title="Movie",
                year="2020",
                display_name="Movie (2020)",
                source_query=title,
            )
        return None


class JobManagerTests(unittest.TestCase):
    def test_create_and_run_rename_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            movie_path = root / "Movie.Name.2020.mkv"
            movie_path.write_bytes(b"video")

            manager = JobManager()
            job = manager.create_job(MODE_RENAME_ONLY, root, FakeTMDB())

            self.assertEqual(len(job.proposals), 1)
            proposal = job.proposals[0]
            self.assertEqual(proposal.target_name, "Movie (2020)")

            manager.set_decision(job.job_id, proposal.movie_id, Decision.ACCEPT)
            manager.run_rename_stage(job.job_id)

            renamed_path = root / "Movie (2020)" / "Movie (2020).mkv"
            self.assertTrue(renamed_path.exists())

    def test_rejects_job_outside_allowed_roots(self) -> None:
        with tempfile.TemporaryDirectory() as allowed_tmp, tempfile.TemporaryDirectory() as other_tmp:
            allowed_root = Path(allowed_tmp)
            other_root = Path(other_tmp)
            (other_root / "Movie.Name.2020.mkv").write_bytes(b"video")

            manager = JobManager(allowed_roots=[allowed_root])
            with self.assertRaises(ValueError):
                manager.create_job(MODE_RENAME_ONLY, other_root, FakeTMDB())


if __name__ == "__main__":
    unittest.main()
