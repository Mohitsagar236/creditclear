"""
System test wrapper script that adds the mock middleware to the Python path.
"""
import os
import sys

# Add the mock middleware to the Python path
mock_middleware_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "utils", "mock_middleware")
sys.path.insert(0, mock_middleware_path)

# Run the system test script
import system_test

if __name__ == "__main__":
    # Print a success message if we make it to the end without errors
    print("\nMock middleware successfully loaded!")
