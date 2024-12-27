import datetime
import inspect
import stat
import sys
import logging
import os
import threading
from crawler.constants.constant import RAW_PATH_CONSTANTS

if sys.platform == "win32":
    os.system('color')


class log:
    __server_instance = None
    __file_handler_added = False
    __lock = threading.Lock()
    __last_cleanup_date = None
    __current_log_file = None
    __current_file_number = 1

    def __configure_logs(self):
        with self.__lock:
            self.__server_instance = logging.getLogger('orion_logs')

            if not self.__server_instance.hasHandlers():
                self.__server_instance.setLevel(logging.INFO)

                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.DEBUG)  # Match the log level

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
        with self.__lock:
            try:
                log_directory = os.path.join(
                    RAW_PATH_CONSTANTS.LOG_DIRECTORY,
                    datetime.datetime.now().strftime("%Y-%m-%d")
                )
                if not os.path.exists(log_directory):
                    os.makedirs(log_directory, exist_ok=True)
                    self.__current_file_number = 1
                    self.__cleanup_old_logs()

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
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
                return line_count
        except FileNotFoundError:
            return 0
        except UnicodeDecodeError as e:
            print(f"Error reading file due to encoding issue: {e}")
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
        log_tag = "[APP-LOG]"
        if include_caller:
            caller_class, caller_file, caller_line = self.get_caller_info()
            return f"{log_tag} {log_type} - {current_time} : {p_log} - {caller_class} ({caller_file}:{caller_line})"
        else:
            return f"{log_tag} {log_type} - {current_time} : {p_log}"

    def i(self, p_log):
        try:
            console_log = self.__format_log_message("INFO", p_log)
            self.__write_to_file(console_log)
            self.__server_instance.info(console_log)
            sys.stdout.flush()

        except Exception:
            pass

    def s(self, p_log):
        try:
            console_log = self.__format_log_message("INFO", p_log)
            self.__server_instance.info(console_log)
            self.__write_to_file(console_log)
            sys.stdout.flush()

        except Exception:
            pass

    def w(self, p_log):
        try:
            console_log = self.__format_log_message("WARNING", p_log)
            self.__server_instance.warning(console_log)
            self.__write_to_file(console_log)
            sys.stdout.flush()

        except Exception:
            pass

    def e(self, p_log):
        try:
            console_log = self.__format_log_message("ERROR", p_log)
            self.__server_instance.error(console_log)
            self.__write_to_file(console_log)
            sys.stdout.flush()

        except Exception:
            pass

    def c(self, p_log):
        try:
            console_log = self.__format_log_message("CRITICAL", p_log)
            self.__server_instance.critical(console_log)
            self.__write_to_file(console_log)
            sys.stdout.flush()

        except Exception:
            pass
