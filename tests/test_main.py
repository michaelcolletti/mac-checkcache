import pytest
import os
import sys
import time
import datetime
import shutil
import tempfile
from unittest.mock import patch, MagicMock, call

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.main import (
    get_dir_size,
    format_size,
    get_last_access_time,
    is_old_cache,
    print_dir_tree,
    analyze_cache_directory,
    interactive_cleanup
)

# Fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def mock_file_structure(temp_dir):
    """Create a mock file structure for testing."""
    # Create directories
    os.makedirs(os.path.join(temp_dir, "dir1", "subdir1"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "dir2"), exist_ok=True)
    
    # Create files with specific sizes
    with open(os.path.join(temp_dir, "file1.txt"), "wb") as f:
        f.write(b"0" * 1024)  # 1KB file
    
    with open(os.path.join(temp_dir, "dir1", "file2.txt"), "wb") as f:
        f.write(b"0" * 2048)  # 2KB file
    
    with open(os.path.join(temp_dir, "dir1", "subdir1", "file3.txt"), "wb") as f:
        f.write(b"0" * 4096)  # 4KB file
    
    with open(os.path.join(temp_dir, "dir2", "file4.txt"), "wb") as f:
        f.write(b"0" * 8192)  # 8KB file
    
    return temp_dir

# Tests for get_dir_size
def test_get_dir_size_file(temp_dir):
    file_path = os.path.join(temp_dir, "testfile.txt")
    with open(file_path, "wb") as f:
        f.write(b"0" * 1024)
    
    assert get_dir_size(file_path) == 0  # Should return 0 for files

def test_get_dir_size_empty_dir(temp_dir):
    assert get_dir_size(temp_dir) == 0

def test_get_dir_size_with_content(mock_file_structure):
    assert get_dir_size(mock_file_structure) == 1024 + 2048 + 4096 + 8192  # 15KB total

def test_get_dir_size_subdir(mock_file_structure):
    dir1_path = os.path.join(mock_file_structure, "dir1")
    assert get_dir_size(dir1_path) == 2048 + 4096  # 6KB total

# Tests for format_size
def test_format_size_bytes():
    assert format_size(500) == "500.00 B"

def test_format_size_kb():
    assert format_size(1024) == "1.00 KB"

def test_format_size_mb():
    assert format_size(1024 * 1024) == "1.00 MB"

def test_format_size_gb():
    assert format_size(1024 * 1024 * 1024) == "1.00 GB"

def test_format_size_tb():
    assert format_size(1024 * 1024 * 1024 * 1024) == "1.00 TB"

# Tests for get_last_access_time
def test_get_last_access_time_file(temp_dir):
    file_path = os.path.join(temp_dir, "testfile.txt")
    with open(file_path, "w") as f:
        f.write("test")
    
    access_time = get_last_access_time(file_path)
    assert isinstance(access_time, datetime.datetime)
    assert (datetime.datetime.now() - access_time).total_seconds() < 10  # Should be recent

def test_get_last_access_time_nonexistent():
    assert get_last_access_time("/nonexistent/path") is None

# Tests for is_old_cache
@patch('src.main.get_last_access_time')
def test_is_old_cache_true(mock_get_last_access):
    old_date = datetime.datetime.now() - datetime.timedelta(days=400)
    mock_get_last_access.return_value = old_date
    assert is_old_cache("/some/path") is True

@patch('src.main.get_last_access_time')
def test_is_old_cache_false(mock_get_last_access):
    recent_date = datetime.datetime.now() - datetime.timedelta(days=10)
    mock_get_last_access.return_value = recent_date
    assert is_old_cache("/some/path") is False

@patch('src.main.get_last_access_time')
def test_is_old_cache_none(mock_get_last_access):
    mock_get_last_access.return_value = None
    assert is_old_cache("/some/path") is False

@patch('src.main.get_last_access_time')
def test_is_old_cache_custom_months(mock_get_last_access):
    three_months_ago = datetime.datetime.now() - datetime.timedelta(days=100)
    mock_get_last_access.return_value = three_months_ago
    assert is_old_cache("/some/path") is False  # Not old with default 12 months
    assert is_old_cache("/some/path", months=2) is True  # Old with 2 months threshold

# Tests for print_dir_tree
@patch('builtins.print')
@patch('src.main.get_dir_size')
@patch('src.main.get_last_access_time')
@patch('src.main.is_old_cache')
def test_print_dir_tree_basic(mock_is_old, mock_get_access, mock_get_size, mock_print, temp_dir):
    mock_get_size.return_value = 1024
    mock_get_access.return_value = datetime.datetime(2023, 1, 1)
    mock_is_old.return_value = False
    print_dir_tree(temp_dir)
    mock_print.assert_called()

@patch('builtins.print')
def test_print_dir_tree_max_depth(mock_print, mock_file_structure):
    print_dir_tree(mock_file_structure, max_depth=1)
    # Just verify it runs without error - full output testing would be complex

@patch('builtins.print')
def test_print_dir_tree_permission_error(mock_print):
    # Test handling of permission error
    non_readable_path = "/root/secret"  # Should trigger permission error
    print_dir_tree(non_readable_path)
    mock_print.assert_called()

# Tests for analyze_cache_directory
@patch('src.main.print_dir_tree')
@patch('src.main.get_dir_size')
def test_analyze_cache_directory_basic(mock_get_size, mock_print_tree, mock_file_structure):
    mock_get_size.return_value = 15360  # 15KB
    result = analyze_cache_directory(mock_file_structure)
    assert mock_print_tree.called
    assert mock_get_size.called

@patch('builtins.print')
def test_analyze_cache_directory_nonexistent(mock_print):
    analyze_cache_directory("/nonexistent/path")
    mock_print.assert_any_call("Directory does not exist: /nonexistent/path")

# Tests for interactive_cleanup
@patch('builtins.input')
@patch('src.main.analyze_cache_directory')
def test_interactive_cleanup_no_old_caches(mock_analyze, mock_input):
    mock_analyze.return_value = []  # No old caches
    interactive_cleanup(["/some/dir"])
    # Should display "No old caches found" message
    mock_input.assert_not_called()

@patch('builtins.input')
@patch('src.main.analyze_cache_directory')
@patch('src.main.os.path.isdir')
@patch('src.main.shutil.rmtree')
@patch('src.main.os.remove')
def test_interactive_cleanup_delete_all(mock_remove, mock_rmtree, mock_isdir, mock_analyze, mock_input):
    # Setup mocks
    old_cache1 = ("/path/to/old_dir", 1024, datetime.datetime(2022, 1, 1))
    old_cache2 = ("/path/to/old_file.txt", 2048, datetime.datetime(2022, 1, 1))
    mock_analyze.return_value = [old_cache1, old_cache2]
    mock_input.return_value = "1"  # Delete all
    mock_isdir.side_effect = lambda path: path == old_cache1[0]
    
    interactive_cleanup(["/some/dir"])
    
    mock_rmtree.assert_called_once_with(old_cache1[0])
    mock_remove.assert_called_once_with(old_cache2[0])

@patch('builtins.input')
@patch('src.main.analyze_cache_directory')
@patch('src.main.os.path.isdir')
@patch('src.main.shutil.rmtree')
@patch('src.main.os.remove')
def test_interactive_cleanup_select_individual(mock_remove, mock_rmtree, mock_isdir, mock_analyze, mock_input):
    old_cache1 = ("/path/to/old_dir", 1024, datetime.datetime(2022, 1, 1))
    old_cache2 = ("/path/to/old_file.txt", 2048, datetime.datetime(2022, 1, 1))
    mock_analyze.return_value = [old_cache1, old_cache2]
    mock_input.side_effect = ["2", "y", "n"]  # Select individual, delete first, keep second
    mock_isdir.side_effect = lambda path: path == old_cache1[0]
    
    interactive_cleanup(["/some/dir"])
    
    mock_rmtree.assert_called_once_with(old_cache1[0])
    mock_remove.assert_not_called()

@patch('builtins.input')
@patch('src.main.analyze_cache_directory')
def test_interactive_cleanup_exit(mock_analyze, mock_input):
    old_cache = ("/path/to/old_dir", 1024, datetime.datetime(2022, 1, 1))
    mock_analyze.return_value = [old_cache]
    mock_input.return_value = "3"  # Exit without deleting
    
    interactive_cleanup(["/some/dir"])
    # Should exit without deletion actions

@patch('builtins.input')
@patch('src.main.analyze_cache_directory')
def test_interactive_cleanup_invalid_option(mock_analyze, mock_input):
    old_cache = ("/path/to/old_dir", 1024, datetime.datetime(2022, 1, 1))
    mock_analyze.return_value = [old_cache]
    mock_input.side_effect = ["invalid", "3"]  # Invalid option, then exit
    
    interactive_cleanup(["/some/dir"])
    
    assert mock_input.call_count == 2  # First invalid, then valid choice