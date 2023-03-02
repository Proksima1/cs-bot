class MyLogger:
    """Класс для логирования событий"""
    def __init__(self):
        self.logger = None

    def start_file_logging(self, logger_name, log_path):
        """Обычное логирование в файл"""
        import logging
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        try:
            fh = logging.FileHandler(log_path)
        except FileNotFoundError:
            log_path = "downloader.log"
            fh = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def start_rotate_logging(self, logger_name, log_path, max_bytes=104857600, story_backup=5):
        """Логирование в файл с ротацией логов"""
        import logging
        from logging.handlers import RotatingFileHandler
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        try:
            fh = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=story_backup)
        except FileNotFoundError:
            log_path = "downloader.log"
            fh = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=story_backup)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def add(self, msg):
        self.logger.info(str(msg))

    def add_error(self, msg):
        self.logger.error(str(msg))
