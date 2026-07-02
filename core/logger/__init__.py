import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    _instance: Optional["Logger"] = None

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._logger: Optional[logging.Logger] = None
        return cls._instance

    def setup(
        self,
        name: str = "nexus",
        level: int = logging.INFO,
        log_file: str | Path | None = None,
        format_string: str | None = None,
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.handlers.clear()

        fmt = format_string or "[%(asctime)s] %(levelname)-8s %(name)s - %(message)s"
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        logger.addHandler(console)

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        self._logger = logger
        return logger

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            self.setup()
        return self._logger  # type: ignore

    def __getattr__(self, name: str):
        return getattr(self.logger, name)
