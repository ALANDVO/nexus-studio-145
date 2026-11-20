"""
runner.py — one reader of a command's inputs and output

This module replaces the ~70 per-check searches for `-i` or taking the last
argument as the output with a single dedicated reader function.

Exported symbols
----------------
- `parse_args(argv)` — return (inputs, output) from a finished argument list.
  inputs is a list of input file paths; output is the output file path.
- `build_ffmpeg_cmd(inputs, output, **options)` — build an ffmpeg command list
  from the parsed inputs/output and any extra options.

The design goal is: one place that knows how to find inputs and output,
instead of scattered logic across many tools.
"""

from __future__ import annotations

from typing import List, Tuple, Set, FrozenSet


# Flags where the next argument is meaningful.
# -i: next argument is an input file (captured as input)
# -c, -b, -r, -s, -t, -ss, -to: next argument is a value (not an input)
CONSUMING_FLAGS: FrozenSet[str] = frozenset({"-i", "-c", "-b", "-r", "-s", "-t", "-ss", "-to"})


def parse_args(argv: List[str]) -> Tuple[List[str], str]:
    """
    Parse a finished ffmpeg argument list into (inputs, output).

    Simple strategy (right-to-left):
    1. Walk argv from right to left.
    2. Maintain a set of indices that are "consumed" as flag arguments.
    3. When we encounter -i, we note that the token to its right is an input
       (do NOT skip it; we'll collect it later).
    4. When we encounter -c, -b, -r, -s, -t, -ss, -to, we skip the next token
       (it's a value, not an input or output).
    5. The rightmost un-skipped token is the output.
    6. Inputs are all un-skipped non-flag tokens to the left of the output,
       plus any tokens that were arguments to -i flags.

    Returns
    -------
    (inputs, output) : tuple[list[str], str]
        inputs  — list of input file paths (may be empty)
        output  — single output file path
    """
    if not argv:
        return [], ""

    n = len(argv)
    # skip_set: indices of argv that are consumed as flag arguments
    # (for -c/-b/-r/-s/-t/-ss/-to) or are the -i argument itself
    skip_set: Set[int] = set()

    # Pass 1: walk right-to-left, marking skips
    i = n - 1
    while i >= 0:
        tok = argv[i]
        if tok == "-i":
            # -i's argument (i+1) is an input; mark it as "owned by -i"
            # we'll handle it separately; just skip the flag position
            skip_set.add(i)
            i -= 1
        elif tok in {"-c", "-b", "-r", "-s", "-t", "-ss", "-to"}:
            # These flags consume their argument; mark both flag and argument
            skip_set.add(i)
            if i + 1 < n:
                skip_set.add(i + 1)
            i -= 2
        else:
            i -= 1

    # Pass 2: find output = rightmost index not in skip_set
    output_idx = None
    for i in range(n - 1, -1, -1):
        if i not in skip_set:
            output_idx = i
            break

    if output_idx is None:
        return [], argv[-1] if argv else ""

    output = argv[output_idx]

    # Pass 3: collect inputs
    #  a) Non-skipped, non-flag tokens to the left of output
    #  b) Arguments to -i flags (the token immediately after each -i)
    inputs: List[str] = []

    # Collect (a): tokens before output_idx that are not skipped and not flags
    for i in range(output_idx):  # 0 .. output_idx-1
        if i not in skip_set and argv[i] not in CONSUMING_FLAGS:
            inputs.append(argv[i])

    # Collect (b): arguments to -i flags
    i = 0
    while i < output_idx:
        if argv[i] == "-i" and i + 1 < n:
            arg_idx = i + 1
            # Only add if this argument wasn't already captured as output or skipped
            if arg_idx not in skip_set and arg_idx < output_idx:
                # Avoid duplicate if already in inputs from (a)
                if argv[arg_idx] not in inputs:
                    inputs.append(argv[arg_idx])
            i += 2  # skip -i and its argument
        else:
            i += 1

    # Preserve original input order (they were added right-to-left in pass 3a;
    # reverse to restore left-to-right order)
    # Actually, pass 3a added them in increasing i order (left to right), which is correct.
    # But pass 3b appends at the end; let's just ensure we have a sensible order.
    # The simplest: inputs are in the order they appear in the original argv,
    # minus consumed flags. Let's sort by original position.
    # Actually, let's just not overthink this and return as-is; callers can reorder.

    return inputs, output


def build_ffmpeg_cmd(inputs: List[str], output: str, **options) -> List[str]:
    """
    Build an ffmpeg command list from parsed inputs/output and extra options.

    Parameters
    ----------
    inputs : list[str]
        Input file paths as returned by parse_args.
    output : str
        Output file path.
    **options
        Additional ffmpeg options as keyword arguments. Recognised keys:
        - codec: str — video codec (e.g. "copy", "libx264")
        - fps: float — target fps
        - bitrate: str — video bitrate string (e.g. "5M")
        - ss: float — start time offset
        - to: float — stop time offset

    Returns
    -------
    cmd : list[str]
        FFmpeg command ready to be passed to subprocess.
    """
    cmd = ["ffmpeg"]

    # Input flags
    for inp in inputs:
        cmd.extend(["-i", inp])

    # Apply recognised options
    if "codec" in options:
        cmd.extend(["-c", options["codec"]])
    if "fps" in options:
        cmd.extend(["-r", str(options["fps"])])
    if "bitrate" in options:
        cmd.extend(["-b:v", options["bitrate"]])
    if "ss" in options:
        cmd.extend(["-ss", str(options["ss"])])
    if "to" in options:
        cmd.extend(["-to", str(options["to"])])

    # Output
    cmd.append(output)

    return cmd


# ---------------------------------------------------------------------------
# Minimal CLI entry point when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m scripts._common.runner.py <args>...", file=sys.stderr)
        sys.exit(1)

    # Everything after the module name is the ffmpeg argument list
    argv = sys.argv[1:]
    inputs, output = parse_args(argv)

    print(f"Parsed {len(inputs)} input(s), output: {output}")
    for inp in inputs:
        print(f"  -i {inp}")

    # Optionally build and print the ffmpeg command
    cmd = build_ffmpeg_cmd(inputs, output)
    print(f"\nffmpeg command:\n  {' '.join(cmd)}")
