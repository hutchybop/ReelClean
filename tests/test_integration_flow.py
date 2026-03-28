"""Integration test for end-to-end job workflow on temp media tree."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from reelclean.core.models import Decision, TmdbMatch
from reelclean.web.job_manager import JobManager, MODE_RENAME_AND_QUALITY


class IntegrationTMDB:
    """Predictable TMDB stub for integration workflow test."""

    def lookup(self, title: str, year_hint: str | None = None) -> TmdbMatch | None:
        if "movie" not in title.lower():
            return None
        return TmdbMatch(
            title="Movie",
            year="2020",
            display_name="Movie (2020)",
            source_query=title,
        )


class IntegrationFlowTests(unittest.TestCase):
    def test_full_rename_cleanup_and_quality_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            movie = root / "Movie.Name.2020.mkv"
            subtitle = root / "Movie.Name.2020.srt"
            extra = root / "notes.txt"

            movie.write_bytes(b"video")
            subtitle.write_text("subs", encoding="utf-8")
            extra.write_text("delete me", encoding="utf-8")

            manager = JobManager(allowed_roots=[root])
            job = manager.create_job(MODE_RENAME_AND_QUALITY, root, IntegrationTMDB())

            self.assertEqual(len(job.proposals), 1)
            proposal = job.proposals[0]
            manager.set_decision(job.job_id, proposal.movie_id, Decision.ACCEPT)

            job = manager.run_rename_stage(job.job_id)
            renamed_movie = root / "Movie (2020)" / "Movie (2020).mkv"
            renamed_subtitle = root / "Movie (2020)" / "Movie (2020).srt"
            self.assertTrue(renamed_movie.exists())
            self.assertTrue(renamed_subtitle.exists())

            selected_ids = [
                item.candidate_id
                for item in job.cleanup_candidates
                if item.path.name == "notes.txt"
            ]

            job = manager.run_cleanup_stage(
                job_id=job.job_id,
                selected_candidate_ids=selected_ids,
                ffprobe_bin="ffprobe",
            )

            self.assertFalse(extra.exists())
            self.assertEqual(job.status, "completed")
            self.assertTrue(job.quality_results)


if __name__ == "__main__":
    unittest.main()
