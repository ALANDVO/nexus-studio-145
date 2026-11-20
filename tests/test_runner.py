"""
tests/test_runner.py — verify runner.py one reader works correctly

Tests that parse_args correctly identifies inputs and output from
ffmpeg-style argument lists, replacing the scattered per-check logic.
"""

from scripts._common.runner import parse_args, build_ffmpeg_cmd


def test_basic_input_output():
    """Simple case: one input, one output."""
    inputs, output = parse_args(["-i", "source.mp4", "output.mp4"])
    assert inputs == ["source.mp4"], f"Expected ['source.mp4'], got {inputs}"
    assert output == "output.mp4", f"Expected 'output.mp4', got {output}"


def test_multiple_inputs():
    """Multiple inputs: -i flags for each."""
    inputs, output = parse_args(["-i", "a.mov", "-i", "b.mov", "out.mp4"])
    assert inputs == ["a.mov", "b.mov"], f"Expected ['a.mov', 'b.mov'], got {inputs}"
    assert output == "out.mp4", f"Expected 'out.mp4', got {output}"


def test_last_arg_is_output():
    """When no -i flags, last argument is the output."""
    inputs, output = parse_args(["source.mkv", "output.mp4"])
    assert inputs == ["source.mkv"], f"Expected ['source.mkv'], got {inputs}"
    assert output == "output.mp4", f"Expected 'output.mp4', got {output}"


def test_no_inputs():
    """Only output, no inputs (edge case)."""
    inputs, output = parse_args(["output.mp4"])
    assert inputs == [], f"Expected [], got {inputs}"
    assert output == "output.mp4", f"Expected 'output.mp4', got {output}"


def test_with_codec_flag():
    """Codec flag should not be mistaken for input."""
    inputs, output = parse_args(["-c", "libx264", "source.mp4", "output.mp4"])
    assert inputs == ["source.mp4"], f"Expected ['source.mp4'], got {inputs}"
    assert output == "output.mp4", f"Expected 'output.mp4', got {output}"


def test_with_fps_flag():
    """FPS flag should not be mistaken for input."""
    inputs, output = parse_args(["-r", "30", "source.mkv", "out.mp4"])
    assert inputs == ["source.mkv"], f"Expected ['source.mkv'], got {inputs}"
    assert output == "out.mp4", f"Expected 'out.mp4', got {output}"


def test_build_ffmpeg_cmd():
    """build_ffmpeg_cmd produces correct command list."""
    cmd = build_ffmpeg_cmd(["source.mp4"], "output.mp4", codec="libx264", fps=30)
    assert cmd == ["ffmpeg", "-i", "source.mp4", "-c", "libx264", "-r", "30", "output.mp4"], \
        f"Unexpected cmd: {cmd}"


def test_build_ffmpeg_cmd_with_bitrate():
    """build_ffmpeg_cmd with bitrate option."""
    cmd = build_ffmpeg_cmd(["vid.mov"], "out.mp4", bitrate="5M", ss=10.0)
    assert "-b:v" in cmd, f"Expected -b:v in cmd: {cmd}"
    assert "-ss" in cmd, f"Expected -ss in cmd: {cmd}"
    assert cmd[-1] == "out.mp4", f"Expected output as last arg: {cmd}"


def test_parse_args_cli_style():
    """CLI-style argument parsing."""
    inputs, output = parse_args(["-i", "input.mov", "-c", "copy", "output.mp4"])
    assert inputs == ["input.mov"], f"Expected ['input.mov'], got {inputs}"
    assert output == "output.mp4", f"Expected 'output.mp4', got {output}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
