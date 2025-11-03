"""
Test runner script
"""
import sys
import pytest


def run_tests():
    """Run test suite"""
    
    # Test arguments
    args = [
        "tests/",
        "-v",                    # Verbose
        "--tb=short",            # Short traceback
        "--color=yes",           # Colored output
        "-m", "not integration"  # Skip integration tests by default
    ]
    
    # Run pytest
    exit_code = pytest.main(args)
    sys.exit(exit_code)


def run_integration_tests():
    """Run integration tests only"""
    
    args = [
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes",
        "-m", "integration"
    ]
    
    exit_code = pytest.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "integration":
        run_integration_tests()
    else:
        run_tests()