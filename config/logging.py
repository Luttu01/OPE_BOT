import logging

from opebot.config.paths import file_path_logs

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(funcName)s] - %(levelname)s - %(message)s',
    filename=file_path_logs
)