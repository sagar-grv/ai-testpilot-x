"""Tests for execution layer."""

from unittest.mock import patch, MagicMock
from schemas.test_result_schema import TestResultSchema


def test_screenshot_utils_capture(tmp_path):
    from core.screenshot_utils import capture_screenshot

    mock_driver = MagicMock()
    mock_driver.save_screenshot.return_value = True
    path = str(tmp_path / "test.png")
    result = capture_screenshot(mock_driver, path)
    assert result == path
    mock_driver.save_screenshot.assert_called_once_with(path)


def test_screenshot_utils_compare_no_pil():
    from core.screenshot_utils import compare_screenshots

    # When PIL not available or files not real, should return 0.5
    result = compare_screenshots("nonexistent1.png", "nonexistent2.png")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_selenium_runner_returns_test_result_schema():
    from execution.runners.selenium_runner import run_test

    code = "def test_TC01(driver):\n    pass\n"
    mock_driver = MagicMock()
    mock_service = MagicMock()
    with (
        patch("execution.runners.selenium_runner.webdriver") as mock_wd,
        patch("execution.runners.selenium_runner.Service", return_value=mock_service),
        patch("execution.runners.selenium_runner.ChromeDriverManager") as mock_mgr,
    ):
        mock_mgr.return_value.install.return_value = "/path/to/chromedriver"
        mock_wd.ChromeOptions.return_value = MagicMock()
        mock_wd.Chrome.return_value = mock_driver
        result = run_test("TC01", code, "https://example.com", headless=True)
    assert isinstance(result, TestResultSchema)
    assert result.tc_id == "TC01"
    assert result.status in ("PASS", "FAIL", "ERROR")


def test_selenium_runner_captures_failure():
    from execution.runners.selenium_runner import run_test

    code = "def test_TC01(driver):\n    raise Exception('Element not found')\n"
    mock_driver = MagicMock()
    with (
        patch("execution.runners.selenium_runner.webdriver") as mock_wd,
        patch("execution.runners.selenium_runner.Service"),
        patch("execution.runners.selenium_runner.ChromeDriverManager"),
    ):
        mock_wd.ChromeOptions.return_value = MagicMock()
        mock_wd.Chrome.return_value = mock_driver
        result = run_test("TC01", code, "https://example.com")
    assert result.status == "FAIL"
    assert "Element not found" in result.error_message


# ── Task 3.3: Selenium Grid ──────────────────────────────────────────────────


def test_check_grid_health_true():
    from execution.grids.selenium_grid import check_grid_health

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("execution.grids.selenium_grid.httpx.get", return_value=mock_resp):
        result = check_grid_health("http://localhost:4444/wd/hub")
    assert result is True


def test_check_grid_health_false_on_exception():
    from execution.grids.selenium_grid import check_grid_health

    with patch(
        "execution.grids.selenium_grid.httpx.get",
        side_effect=Exception("Connection refused"),
    ):
        result = check_grid_health("http://localhost:4444/wd/hub")
    assert result is False
