"""
fit.py — reframe/crop video using ffmpeg

Resizes and crops video to target dimensions using ffmpeg scaling and
crop filters. Supports `--fit cover` (scale to cover, crop excess) and
`--fit contain` (scale to fit, letterbox).

Exported symbols
----------------
- `fit_video(inputs, output, fit_mode, **options)` — run ffmpeg to reframe
  video according to fit_mode.

The design goal is: provide a dedicated reframe tool instead of
scattered per-tool crop logic.
"""

from __future__ import annotations

from scripts._common.runner import build_ffmpeg_cmd


def fit_video(inputs: list[str], output: str, fit_mode: str = "cover", **options) -> list[str]:
    """
    Build and run an ffmpeg command to reframe video.

    Parameters
    ----------
    inputs : list of str
        Input file paths (typically one source file).
    output : str
        Output file path.
    fit_mode : str, optional
        "cover" — scale to cover target dimensions (crop excess),
        "contain" — scale to fit target dimensions (letterbox).
        Default "cover".
    **options
        Additional ffmpeg options passed through to the command.

    Returns
    -------
    list[str]
        The ffmpeg command that was executed (for logging/inspection).
    """
    if fit_mode not in ("cover", "contain"):
        raise ValueError(f"Invalid fit_mode '{fit_mode}'; expected 'cover' or 'contain'")

    # Determine scale/resize parameters based on fit_mode
    # For now, use a simple approach: scale to target then crop/letterbox
    # The actual scale values will be supplied by the caller or derived
    filter_str = _fit_filter(fit_mode, **options)

    cmd = build_ffmpeg_cmd(inputs, output, vf=filter_str, **options)
    return cmd


def _fit_filter(fit_mode: str, **options) -> str:
    """Return the ffmpeg video filter string for the given fit mode."""
    # Target dimensions from options, or defaults
    target_w = options.get("width", 1920)
    target_h = options.get("height", 1080)

    if fit_mode == "cover":
        # Scale to cover: scale keeping aspect, then crop to exact size
        # Scale: scale=W:H where W/H maintain ratio but cover target
        # Use "iw*min(target_w/iw/ih,target_h/ih):ih*min(target_w/iw/ih,target_h/ih)"
        # then crop to exact target
        return f"scale=iw*max({target_w}/iw,{target_h}/ih):ih*max({target_w}/iw,{target_h}/ih):0,crop={target_w}:{target_h}:(iw-{target_w})/2:(ih-{target_h})/2"
    else:  # contain
        # Scale to fit: scale keeping aspect, letterbox the rest
        # Scale to fit within target while maintaining aspect
        return f"scale=iw*min({target_w}/iw,{target_h}/ih):ih*min({target_w}/iw,{target_h}/ih),pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2"


# ---------------------------------------------------------------------------
# Minimal CLI entry point when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python -m scripts._common.fit <input> <output> <fit_mode> [width height]")
        print("  fit_mode: cover | contain")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    fit_mode = sys.argv[3]
    width = int(sys.argv[4]) if len(sys.argv) > 4 else 1920
    height = int(sys.argv[5]) if len(sys.argv) > 5 else 1080

    cmd = fit_video([input_file], output_file, fit_mode=fit_mode, width=width, height=height)
    print(f"\nffmpeg command:\n  {' '.join(cmd)}")
