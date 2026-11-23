"""
tests/test_fit.py — verify fit.py reframe/crop works correctly

Tests that fit_video correctly builds ffmpeg commands for reframe operations.
"""

from scripts._common.fit import fit_video


def test_fit_cover_default():
    """fit_video with cover mode uses default 1920x1080."""
    cmd = fit_video(["source.mp4"], "output.mp4", fit_mode="cover")
    assert "-i" in cmd, f"Expected -i in cmd: {cmd}"
    assert "output.mp4" in cmd, f"Expected output.mp4 in cmd: {cmd}"
    # Cover mode should have crop filter in the vf string
    vf_idx = cmd.index("-vf") + 1
    vf_filter = cmd[vf_idx]
    assert "crop" in vf_filter, f"Expected crop filter in cover mode vf: {vf_filter}"


def test_fit_contain_default():
    """fit_video with contain mode uses default 1920x1080."""
    cmd = fit_video(["source.mp4"], "output.mp4", fit_mode="contain")
    assert "-i" in cmd, f"Expected -i in cmd: {cmd}"
    assert "output.mp4" in cmd, f"Expected output.mp4 in cmd: {cmd}"
    # Contain mode should have pad filter in the vf string
    vf_idx = cmd.index("-vf") + 1
    vf_filter = cmd[vf_idx]
    assert "pad" in vf_filter, f"Expected pad filter in contain mode vf: {vf_filter}"


def test_fit_cover_custom_size():
    """fit_video with cover mode and custom size."""
    cmd = fit_video(["source.mov"], "out.mp4", fit_mode="cover", width=1280, height=720)
    assert "-i" in cmd, f"Expected -i in cmd: {cmd}"
    assert "out.mp4" in cmd, f"Expected out.mp4 in cmd: {cmd}"
    # Cover mode should have crop filter in the vf string
    vf_idx = cmd.index("-vf") + 1
    vf_filter = cmd[vf_idx]
    assert "crop" in vf_filter, f"Expected crop filter in cover mode vf: {vf_filter}"
    # Should reference the custom dimensions
    assert "1280" in vf_filter or "720" in vf_filter, \
        f"Expected custom dimensions in vf filter: {vf_filter}"


def test_fit_contain_custom_size():
    """fit_video with contain mode and custom size."""
    cmd = fit_video(["vid.mkv"], "out.mp4", fit_mode="contain", width=854, height=480)
    assert "-i" in cmd, f"Expected -i in cmd: {cmd}"
    assert "out.mp4" in cmd, f"Expected out.mp4 in cmd: {cmd}"
    # Contain mode should have pad filter in the vf string
    vf_idx = cmd.index("-vf") + 1
    vf_filter = cmd[vf_idx]
    assert "pad" in vf_filter, f"Expected pad filter in contain mode vf: {vf_filter}"
    # Should reference the custom dimensions
    assert "854" in vf_filter or "480" in vf_filter, \
        f"Expected custom dimensions in vf filter: {vf_filter}"


def test_fit_invalid_mode():
    """fit_video raises ValueError for invalid mode."""
    try:
        fit_video(["src.mp4"], "out.mp4", fit_mode="invalid")
        assert False, "Expected ValueError for invalid fit_mode"
    except ValueError as e:
        assert "Invalid fit_mode" in str(e)


def test_fit_with_codec():
    """fit_video works alongside codec options."""
    cmd = fit_video(["input.mp4"], "output.mp4", fit_mode="cover", codec="libx264", fps=30)
    assert "-i" in cmd
    assert "output.mp4" in cmd
    # Check vf filter contains crop
    vf_idx = cmd.index("-vf") + 1
    vf_filter = cmd[vf_idx]
    assert "crop" in vf_filter


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
