import logging
from pathlib import Path


# Assume this file lives in project-root/src/newsfeed/utils/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Logs will go in the root-level "logs" directory
LOG_DIR = PROJECT_ROOT/ "logs"

# Ensure the logs directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logging():
    """
    Configure logging for the application.

    Logs are written to:
      - logs/newsfeed.log (file)
      - Console (standard output)
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Write log messages to the newsfeed file in the logs/ directory
    file_handler = logging.FileHandler(LOG_DIR / "newsfeed.log")
    file_handler.setLevel(logging.DEBUG)  # Keep DEBUG logs in the file
    file_handler.setFormatter(formatter)

    # Also display log messages in the terminal (stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # Only show INFO+ in terminal
    stream_handler.setFormatter(formatter)


    # Log levels:
    # DEBUG    - Detailed debug information, useful for development
    # INFO     - General events, confirming things are working as expected
    # WARNING  - Unexpected events, but the program is still running
    # ERROR    - Serious problems, parts of the app may not work
    # CRITICAL - Very severe errors, the program may be unable to continue

    logging.basicConfig(
        level=logging.INFO,
        # Log format, e.g. "2025-07-22 13:45:12,345 - newsfeed.cli - INFO - CLI started"
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            file_handler, 
            stream_handler
            ]
    )