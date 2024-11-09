import datetime
import inspect
import stat
import sys
import logging
import os
from termcolor import colored
from threading import Lock
from crawler.constants.constant import RAW_PATH_CONSTANTS

if sys.platform == "win32":
    os.system('color')


class log:
    __server_instance = None
    __file_handler_added = False
    __lock = Lock()
    __last_cleanup_date = None
    __current_log_file = None  # Track current log file path
    __current_file_number = 1  # Track current file number

    def __configure_logs(self):
        with self.__lock:
            self.__server_instance = logging.getLogger('genesis_logs')

            if not self.__server_instance.hasHandlers():
                self.__server_instance.setLevel(logging.DEBUG)

                if not os.path.exists(RAW_PATH_CONSTANTS.LOG_DIRECTORY):
                    os.makedirs(RAW_PATH_CONSTANTS.LOG_DIRECTORY)

                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)

                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(formatter)

                self.__server_instance.addHandler(console_handler)

            self.__server_instance.propagate = False

    @staticmethod
    def g():
        if log.__server_instance is None:
            log()
        return log.__server_instance

    def __init__(self):
        log.__server_instance = self
        self.__configure_logs()

    def get_caller_info(self):
        frame = inspect.currentframe()
        while frame:
            frame = frame.f_back
            if frame:
                caller_class = frame.f_locals.get("self", None)
                if caller_class and caller_class.__class__.__name__ != self.__class__.__name__:
                    caller_class = caller_class.__class__.__name__
                    caller_file = os.path.abspath(frame.f_code.co_filename)
                    caller_line = frame.f_lineno
                    return caller_class, caller_file, caller_line
                elif not caller_class:
                    caller_file = os.path.abspath(frame.f_code.co_filename)
                    caller_line = frame.f_lineno
                    return "Function", caller_file, caller_line
        return "Unknown", "Unknown", 0

    def __write_to_file(self, log_message, lines_per_file=10000):
        try:
            log_directory = os.path.join(
                RAW_PATH_CONSTANTS.LOG_DIRECTORY,
                datetime.datetime.now().strftime("%Y-%m-%d")
            )
            if not os.path.exists(log_directory):
                os.makedirs(log_directory, exist_ok=True)
                self.__current_file_number = 1  # Reset counter for a new day
                self.__cleanup_old_logs()  # Cleanup only on new day folder creation

            if self.__current_log_file is None:
                self.__set_current_log_file(log_directory)

            if self.__get_line_count(self.__current_log_file) >= lines_per_file:
                self.__current_file_number += 1
                self.__current_log_file = os.path.join(
                    log_directory, f"log_{self.__current_file_number}.log"
                )

            caller_class, caller_file, caller_line = self.get_caller_info()
            full_log_message = f"{log_message} - {caller_class} ({caller_file}:{caller_line})"

            with open(self.__current_log_file, 'a') as log_file:
                log_file.write(full_log_message + "\n")

            os.chmod(self.__current_log_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

        except Exception as e:
            print(f"Error writing to log: {e}")

    def __set_current_log_file(self, log_directory):
        log_files = sorted([f for f in os.listdir(log_directory)
                            if f.startswith("log_") and f.endswith(".log")])

        if log_files:
            last_log_file = log_files[-1]
            self.__current_file_number = int(last_log_file.split('_')[1].split('.')[0])
            self.__current_log_file = os.path.join(log_directory, last_log_file)
        else:
            self.__current_log_file = os.path.join(log_directory, "log_1.log")
            self.__current_file_number = 1

    def __get_line_count(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return sum(1 for _ in f)
        except FileNotFoundError:
            return 0

    def __cleanup_old_logs(self, retention_days=30):
        try:
            now = datetime.datetime.now().date()
            if log.__last_cleanup_date == now:
                return

            log.__last_cleanup_date = now  # Update last cleanup date
            cutoff_date = now - datetime.timedelta(days=retention_days)

            for log_dir in os.listdir(RAW_PATH_CONSTANTS.LOG_DIRECTORY):
                log_path = os.path.join(RAW_PATH_CONSTANTS.LOG_DIRECTORY, log_dir)
                if os.path.isdir(log_path):
                    try:
                        log_date = datetime.datetime.strptime(log_dir, "%Y-%m-%d").date()
                        if log_date < cutoff_date:
                            for file in os.listdir(log_path):
                                os.remove(os.path.join(log_path, file))
                            os.rmdir(log_path)
                    except ValueError:
                        continue

        except Exception as e:
            print(f"Error during log cleanup: {e}")

    def __format_log_message(self, log_type, p_log, include_caller=False):
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if include_caller:
            caller_class, caller_file, caller_line = self.get_caller_info()
            return f"{log_type} - {current_time} : {p_log} - {caller_class} ({caller_file}:{caller_line})"
        else:
            return f"{log_type} - {current_time} : {p_log}"

    def i(self, p_log):
        try:
            console_log = self.__format_log_message("INFO", p_log)
            self.__write_to_file(console_log)
            print(colored(console_log, 'cyan', attrs=['bold']))
        except Exception:
            pass

    def s(self, p_log):
        try:
            console_log = self.__format_log_message("SUCCESS", p_log)
            self.__write_to_file(console_log)
            print(colored(console_log, 'green'))
        except Exception:
            pass

    def w(self, p_log):
        try:
            console_log = self.__format_log_message("WARNING", p_log)
            self.__server_instance.warning(console_log)
            self.__write_to_file(console_log)
            print(colored(console_log, 'yellow'))
        except Exception:
            pass

    def e(self, p_log):
        try:
            console_log = self.__format_log_message("ERROR", p_log)
            self.__server_instance.error(console_log)
            self.__write_to_file(console_log)
            print(colored(console_log, 'blue'))
        except Exception:
            pass

    def c(self, p_log):
        try:
            console_log = self.__format_log_message("CRITICAL", p_log)
            self.__server_instance.critical(console_log)
            self.__write_to_file(console_log)
            print(colored(console_log, 'red'))
        except Exception:
            pass
