import os
import sys

# Print Python version and path
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")

try:
    from PyPDF2 import PdfMerger
    print("Successfully imported PdfMerger from PyPDF2")
except ImportError as e:
    print(f"Error importing PdfMerger: {str(e)}")
    
    try:
        from PyPDF2 import PdfFileMerger
        print("Successfully imported PdfFileMerger from PyPDF2 (older version)")
    except ImportError as e:
        print(f"Error importing PdfFileMerger: {str(e)}")
        
        try:
            import PyPDF2
            print(f"PyPDF2 version: {PyPDF2.__version__}")
            print(f"Available in PyPDF2: {dir(PyPDF2)}")
        except ImportError as e:
            print(f"Error importing PyPDF2: {str(e)}")

# Try to create an empty temp directory structure
print("\nTesting file system access:")
temp_dir = os.path.abspath("temp_test")
print(f"Creating test directory: {temp_dir}")

try:
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Successfully created directory: {temp_dir}")
    
    # Try to create a simple file
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("Test file")
    
    print(f"Successfully created file: {test_file}")
    
    # Check if file exists
    if os.path.exists(test_file):
        print(f"File exists: {test_file}")
    else:
        print(f"File does not exist: {test_file}")
    
    # Clean up
    os.remove(test_file)
    os.rmdir(temp_dir)
    print("Successfully cleaned up test directory")
    
except Exception as e:
    print(f"Error testing file system: {str(e)}")

print("\nTest complete!") 