# tests/test_url_validator.py
import pytest
from utils.url_validator import URLValidator


def test_url_format():
    """Test URL formatting"""
    assert URLValidator.format_url("example.com") == "https://example.com"
    assert URLValidator.format_url("https://example.com") == "https://example.com"
    assert URLValidator.format_url("http://example.com") == "http://example.com"
    assert URLValidator.format_url("") == ""


def test_url_validation():
    """Test URL validation"""
    assert URLValidator.is_valid_url("https://example.com") == True
    assert URLValidator.is_valid_url("http://example.com") == True
    assert URLValidator.is_valid_url("not_a_url") == False
    assert URLValidator.is_valid_url("") == False


@pytest.mark.parametrize("url,expected_status", [
    ("https://www.google.com", "Success"),
    ("https://thisisnotarealwebsite.com", "Failed"),
])
def test_url_processing(url, expected_status):
    """Test URL processing with different URLs"""
    result = URLValidator.process_url(url, 1)
    assert result['url'] == url
    assert result['status'] in ['Success', 'Failed']
    assert 'load_time' in result
    assert 'error' in result
    assert 'timestamp' in result
    assert 'steps' in result


def test_screenshot_capture(mocker):
    """Test screenshot capture functionality"""
    mock_driver = mocker.Mock()
    mock_driver.get_screenshot_as_png.return_value = b"fake_screenshot"

    screenshot = URLValidator.capture_screenshot_base64(mock_driver)
    assert screenshot is not None
    assert isinstance(screenshot, str)


def test_excel_report_generation(tmp_path):
    """Test Excel report generation"""
    results = [
        {
            'url': 'https://example.com',
            'status': 'Success',
            'load_time': 1000,
            'error': None,
            'timestamp': '2024-01-01 12:00:00'
        }
    ]

    report_path = URLValidator.generate_excel_report(results)
    assert report_path.endswith('.xlsx')
    assert os.path.exists(report_path)