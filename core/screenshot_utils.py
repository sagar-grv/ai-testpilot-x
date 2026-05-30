"""Screenshot capture and comparison utilities."""

from monitoring.logger import get_logger

log = get_logger(__name__)


def capture_screenshot(driver, path: str) -> str:
    """Save screenshot to path, return path."""
    driver.save_screenshot(path)
    log.debug(f"Screenshot saved: {path}")
    return path


def compare_screenshots(before: str, after: str) -> float:
    """Return similarity score 0.0-1.0 using pixel diff. Returns 0.5 if PIL unavailable."""
    try:
        from PIL import Image
        import numpy as np

        img_a = np.array(Image.open(before).convert("RGB"))
        img_b = np.array(Image.open(after).convert("RGB"))
        if img_a.shape != img_b.shape:
            return 0.5
        diff = np.abs(img_a.astype(float) - img_b.astype(float))
        similarity = 1.0 - (diff.mean() / 255.0)
        return float(similarity)
    except ImportError:
        return 0.5
    except Exception as e:
        log.warning(f"compare_screenshots failed: {e}")
        return 0.5
