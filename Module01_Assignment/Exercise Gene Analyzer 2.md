# Questions/Discussions

1. Is the filename hardcoded?

The program prompts the user to enter the file path dynamically and therefore it is not hardcoded. Path is formatted for Windows compatibility.

2. How to increase the speed of testing?

To speed up testing, we could use a smaller sample instead of the full 7GB file, enable multi-threaded processing with "dask" instead of using pandas, or use "pickle" instead of reloading CSV each time.

3. What happens if no input file is provided?

When no input file is provided, the user will receive a message saying "\❌ Error: File not found. Please check the file path and try again."

4. What happens if the input file contains an error?

If the input file contains an error, a generic exception is thrown "❌ Error: {e}".

5. How to document the software?

Proper documentation for the software should include docstrings within functions, markdown files explaining things like installation, expected input/output, and dependencies, and inline comments for complex logic.

6. How to track changes?

Use Git for version control and properly annotated commits. 

7. How could the software be delivered to clients?

This software could be delivered to clients using an executable (.exe) or (.app) utilizing pyinstaller. Other options include using a docker container, cloud-based deployment, or packaging the software as a Python module.

8. How could the software be updated (on client environment)?

Software could be updated using Git to push the newest version. We could also automate updates using an auto-updating script to check for changes.

9. What is a good way to prevent bugs after an update?

Some good practices to prevent bugs might include unit testing, automatic testing with CI/CD Pipeline, error logging modules, and beta testing before full release.