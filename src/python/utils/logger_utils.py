import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Return module-scoped logger with unified format and file output.

    Log path mirrors dotted name under ./logs, e.g. utils.document -> logs/utils/document.log
    """
    log_path = os.path.join("logs", *name.split(".")) + ".log"
    log_dir = os.path.dirname(log_path)
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    return logger
