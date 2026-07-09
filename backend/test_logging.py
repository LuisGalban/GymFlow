import os
import sys
import logging
import unittest
import json
from logging.handlers import TimedRotatingFileHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app, logger, LOG_FILE


class TestLoggingConfiguration(unittest.TestCase):

    def test_1_timed_rotating_file_handler_configured(self):
        """RED->GREEN: Logger must have a TimedRotatingFileHandler"""
        test_logger = logging.getLogger("app.main")
        # Check the logger's own handlers or propagate to root
        found = any(isinstance(h, TimedRotatingFileHandler) for h in logging.getLogger().handlers)
        self.assertTrue(found, "No TimedRotatingFileHandler found on root logger")

    def test_2_log_file_exists(self):
        """RED->GREEN: Log file must exist after module import"""
        self.assertTrue(os.path.exists(LOG_FILE), f"Log file {LOG_FILE} does not exist")

    def test_3_logger_writes_info(self):
        """RED->GREEN: logger.info() must write to the log file"""
        test_msg = "TEST_LOG_MESSAGE_F21"
        logger.info(test_msg)

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(test_msg, content, f"Log file does not contain test message: {content[-500:]}")

    def test_4_logger_writes_error(self):
        """RED->GREEN: logger.error() must write to the log file"""
        test_msg = "TEST_ERROR_MESSAGE_F21"
        logger.error(test_msg)

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(test_msg, content, f"Log file does not contain error message: {content[-500:]}")

    def test_5_log_format_contains_timestamp_level_and_name(self):
        """RED->GREEN: Log format must include asctime, name, levelname, message"""
        test_msg = "TEST_FORMAT_CHECK_F21"
        logger.info(test_msg)

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        matching_lines = [l for l in lines if test_msg in l]
        self.assertTrue(len(matching_lines) > 0, "No matching log line found")

        line = matching_lines[-1]
        self.assertIn(" - INFO - ", line, f"Log line missing levelname INFO: {line}")
        self.assertIn(" - app.main - ", line, f"Log line missing logger name: {line}")
        self.assertRegex(line, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", f"Log line missing timestamp: {line}")

    def test_6_root_handler_level_is_info(self):
        """GREEN: Root logger level should be INFO or lower"""
        root_logger = logging.getLogger()
        self.assertLessEqual(root_logger.level, logging.INFO,
                             f"Root logger level {root_logger.level} is higher than INFO")


if __name__ == "__main__":
    unittest.main()
