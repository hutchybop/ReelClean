"""Apply rename and cleanup operations."""

from __future__ import annotations

from pathlib import Path

from .models import (
    CleanupCandidate,
    CleanupKind,
    Decision,
    ExecutionResult,
    OperationResult,
    ProposalStatus,
    RenameProposal,
)


def _is_within_root(path: Path, safe_root: Path) -> bool:
    """Return True when path is inside safe_root."""

    try:
        resolved_path = path.resolve(strict=False)
        resolved_root = safe_root.resolve(strict=False)
        resolved_path.relative_to(resolved_root)
        return True
    except (ValueError, OSError, RuntimeError):
        return False


def _rename_path(
    source: Path,
    target: Path,
    kind: str,
    allow_overwrite: bool,
    safe_root: Path | None,
) -> OperationResult:
    if safe_root and (not _is_within_root(source, safe_root) or not _is_within_root(target, safe_root)):
        return OperationResult(
            kind=kind,
            source=source,
            target=target,
            status="failed",
            message="Path is outside allowed root",
        )

    if not source.exists():
        return OperationResult(
            kind=kind,
            source=source,
            target=target,
            status="failed",
            message="Source path does not exist",
        )

    if source == target:
        return OperationResult(
            kind=kind,
            source=source,
            target=target,
            status="skipped",
            message="Source already matches target",
        )

    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not allow_overwrite:
        return OperationResult(
            kind=kind,
            source=source,
            target=target,
            status="failed",
            message="Target path already exists",
        )

    try:
        source.rename(target)
    except OSError as exc:
        return OperationResult(
            kind=kind,
            source=source,
            target=target,
            status="failed",
            message=str(exc),
        )

    return OperationResult(
        kind=kind,
        source=source,
        target=target,
        status="success",
        message="Renamed successfully",
    )


def _delete_candidate(candidate: CleanupCandidate) -> OperationResult:
    path = candidate.path

    if not path.exists():
        return OperationResult(
            kind="cleanup",
            source=path,
            target=None,
            status="skipped",
            message="Path already removed",
        )

    try:
        if candidate.kind == CleanupKind.EMPTY_FOLDER:
            path.rmdir()
        else:
            path.unlink()
    except OSError as exc:
        return OperationResult(
            kind="cleanup",
            source=path,
            target=None,
            status="failed",
            message=str(exc),
        )

    return OperationResult(
        kind="cleanup",
        source=path,
        target=None,
        status="success",
        message="Deleted successfully",
    )


def execute_plan(
    proposals: list[RenameProposal],
    cleanup_candidates: list[CleanupCandidate],
    allow_overwrite: bool = False,
    safe_root: Path | None = None,
) -> ExecutionResult:
    """Apply accepted rename proposals and selected cleanup deletions."""

    result = ExecutionResult()

    for proposal in proposals:
        if proposal.decision != Decision.ACCEPT:
            continue

        if proposal.status in {ProposalStatus.CONFLICT, ProposalStatus.NEEDS_REVIEW}:
            result.rename_operations.append(
                OperationResult(
                    kind="rename_movie",
                    source=proposal.source_movie_path,
                    target=proposal.target_movie_path,
                    status="failed",
                    message=proposal.conflict_reason or "Proposal is not ready",
                )
            )
            continue

        if proposal.target_movie_path is None:
            result.rename_operations.append(
                OperationResult(
                    kind="rename_movie",
                    source=proposal.source_movie_path,
                    target=None,
                    status="failed",
                    message="Missing target movie path",
                )
            )
            continue

        movie_result = _rename_path(
            source=proposal.source_movie_path,
            target=proposal.target_movie_path,
            kind="rename_movie",
            allow_overwrite=allow_overwrite,
            safe_root=safe_root,
        )
        result.rename_operations.append(movie_result)

        if movie_result.status == "failed":
            continue

        for source_sub, target_sub in zip(
            proposal.source_subtitle_paths,
            proposal.target_subtitle_paths,
        ):
            subtitle_result = _rename_path(
                source=source_sub,
                target=target_sub,
                kind="rename_subtitle",
                allow_overwrite=allow_overwrite,
                safe_root=safe_root,
            )
            result.rename_operations.append(subtitle_result)

    for candidate in cleanup_candidates:
        if not candidate.selected:
            continue

        if safe_root and not _is_within_root(candidate.path, safe_root):
            result.cleanup_operations.append(
                OperationResult(
                    kind="cleanup",
                    source=candidate.path,
                    target=None,
                    status="failed",
                    message="Path is outside allowed root",
                )
            )
            continue

        result.cleanup_operations.append(_delete_candidate(candidate))

    return result
