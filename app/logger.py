import logging

logging.basicConfig(level=logging.INFO,
                    filename=".log",
                    filemode="w",
                    format="[%(asctime)s] [%(levelname)s] %(message)s")

_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"

_handler = logging.FileHandler(".log")
_handler.setFormatter(logging.Formatter(_FORMAT))

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
logger.addHandler(_handler)
