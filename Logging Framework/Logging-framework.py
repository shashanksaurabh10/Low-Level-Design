# REquirenments

# 1. The logging framework should support different log levels, such as DEBUG, INFO, WARNING, ERROR, FATAL
# 2. It should allow logging messages with time stamp, log level, message content
# 3. The framework should support multiple ouput destinations, such as file, console, database
# 4. It should provide a configuarable mechanism to set the log level and output destination
# 5. The logging framework should be thread safe to handle concurrent logging from multiple threads 
# 6. It should be extensible to accomodate new log levels and output destinations in the future

from enum import Enum
import threading
from datetime import datetime
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional

class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5

    def is_greater_or_equal(self, other: 'LogLevel'):
        return self.value >= other.value
    
class LogMessage:
    def __init__(self, level: LogLevel, logger_name: str, message: str):
        self.timestamp = datetime.now()
        self.level = level
        self.logger_name = logger_name
        self.message = message
        self.thread_name = threading.current_thread().name

    def get_timestamp(self):
        return self.timestamp
    
    def get_level(self):
        return self.level
    
    def get_logger_name(self):
        return self.logger_name
    
    def get_message(self):
        return self.message
    
    def get_thread_name(self):
        return self.thread_name
    
class LogFormatter(ABC):
    @abstractmethod
    def format(self, log_message: LogMessage):
        pass

class SimpleTextFormatter(LogFormatter):
    def format(self, log_message: LogMessage):
        timestamp_str = log_message.get_timestamp().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return f"{timestamp_str} [{log_message.get_thread_name()}] {log_message.get_level().name} - {log_message.get_logger_name()}: {log_message.get_message()}\n"
    
class LogAppender(ABC):
    @abstractmethod
    def append(self, log_message: LogMessage):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_formatter(self):
        pass

    @abstractmethod
    def set_formatter(self, formatter: LogFormatter):
        pass

class ConsoleAppender(LogAppender):
    def __init__(self):
        self.formatter = SimpleTextFormatter()

    def append(self, log_message: LogMessage):
        print(self.formatter.format(log_message))

    def close(self):
        pass

    def get_formatter(self):
        return self.formatter
    
    def set_formatter(self, formatter: LogFormatter):
        self.formatter = formatter

class FileAppender(LogAppender):
    def __init__(self, file_path: str):
        self.formattter = SimpleTextFormatter()
        self._lock = threading.Lock()
        try:
            self.writer = open(file_path, 'a')
        except Exception as e:
            print(f"Failed to create writer for file logs, exception: {e}")
            self.writer = None

    def append(self, log_message: LogMessage):
        with self._lock:
            if self.writer:
                try:
                    self.writer.write(self.formattter.format(log_message) + "\n")
                    self.writer.flush()
                except Exception as e:
                    print(f"Failed to write logs to file, exception: {e}")
    
    def close(self):
        if self.writer:
            try:
                self.writer.close()
            except Exception as e:
                print(f"Failed to close the file, exception {e}")

    def set_formatter(self, formatter: LogFormatter):
        self.formattter = formatter

    def get_formatter(self):
        return self.formattter


class AsyncLogProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="AsyncLogProcessor")
        self.shutdown_flag = False

    def process(self, log_message: LogMessage, appenders: list[LogAppender]):
        if self.shutdown_flag:
            print("Logger. is shudown. Cannot process log message")
            return
        def process_task():
            for appender in appenders:
                appender.append(log_message)
        self.executor.submit(process_task)

    def stop(self):
        self.shutdown_flag= True
        self.executor.shutdown(wait=True, timeout=2)
        if not self.executor._shutdown:
            print("Logger executor did not terminate in the specified time.")


class Logger:
    def __init__(self, name: str, parent: Optional['Logger']):
        self.name = name
        self.parent = parent
        self.appenders: List[LogAppender] = []
        self.level: Optional[LogLevel] = None
        self.additivity = True

    def add_appenders(self, appender: LogAppender):
        self.appenders.append(appender)

    def get_appenders(self):
        return self.appenders
    
    def set_level(self, level: LogLevel):
        self.level = level

    def set_additivity(self, additivity):
        self.additivity = additivity

    def get_effective_level(self):
        logger = self
        while logger is not None:
            current_level = logger.level
            if current_level is not None:
                return current_level
            logger = logger.parent
        return LogLevel.DEBUG
    
    def log(self, message_level: LogLevel, message: str):
        if message_level.is_greater_or_equal(self.get_effective_level()):
            log_message = LogMessage(message_level, self.name, message)
            self._call_appenders(log_message)

    def _call_appenders(self, log_message: LogMessage):
        if self.appenders:
            LogManager.get_instance().get_processor().process(log_message, self.appenders)

        if self.additivity and self.parent is not None:
            self.parent._call_appenders(log_message)

    def debug(self, message: str):
        self.log(LogLevel.DEBUG, message)

    def info(self, message: str):
        self.log(LogLevel.INFO, message)

    def warn(self, message: str):
        self.log(LogLevel.WARN, message)

    def error(self, message: str):
        self.log(LogLevel.ERROR, message)

    def fatal(self, message: str):
        self.log(LogLevel.FATAL, message)

class LogManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if LogManager._instance is not None:
            raise Exception("This class is singleton")
        self.loggers: Dict[str, 'Logger'] = {}
        self.root_logger = Logger("root", None)
        self.loggers["root"] = self.root_logger
        self.processor = AsyncLogProcessor()

    @staticmethod
    def get_instance():
        if LogManager._instance is None:
            with LogManager._lock:
                if LogManager._instance is None:
                    LogManager._instance = LogManager()
        return LogManager._instance
    
    def get_logger(self, name: str):
        if name not in self.loggers:
            self.loggers[name] = self._create_logger(name)
        return self.loggers[name]
    
    def _create_logger(self, name: str):
        if name == "root":
            return self.root_logger
        last_dot = name.rfind(".")
        parent_name = "root" if last_dot is -1 else name[:last_dot]
        parent = self.get_logger(parent_name)
        return Logger(name, parent)
    
    def get_root_logger(self):
        return self.root_logger
    
    def get_processor(self):
        return self.processor
    
    def shutdown(self):
        self.processor.stop()

        all_appenders = set()
        for logger in self.loggers.values():
            for appender in logger.get_appenders():
                all_appenders.add(appender)

        for appender in all_appenders:
            appender.close()

        print("Logging framework shut down gracefully.")
