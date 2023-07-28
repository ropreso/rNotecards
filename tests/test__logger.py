"""
deals with logging for the program
"""


def test__logging_01():
    import logging
    from rNotecards.logger import Logger
    from rNotecards.constants import PROJECT_ROOT_DIR
    from pathlib import Path

    log_file_full_path = PROJECT_ROOT_DIR / 'tests' / 'log' / 'app_01.log'
    log_level_file = getattr(logging, 'DEBUG')
    log_level_console = getattr(logging, 'INFO')

    for file in Path(log_file_full_path.parent).glob("*"):
        file.unlink()

    test_logger_01 = Logger.setup_logger(log_file_full_path, log_level_file, log_level_console)
    test_logger_01.error('THIS IS AN ERROR')
    test_logger_01.warning('THIS IS AN WARNING')
    test_logger_01.info('THIS IS INFO')
    test_logger_01.debug('THIS IS A LOT OF INFO')

    # Read log file and split into lines
    with open(log_file_full_path, "r") as f:
        log_lines = f.read().splitlines()

    # Check that each log message appears in the log file
    assert 'THIS IS AN ERROR' in log_lines[-4]
    assert 'THIS IS AN WARNING' in log_lines[-3]
    assert 'THIS IS INFO' in log_lines[-2]
    assert 'THIS IS A LOT OF INFO' in log_lines[-1]


def test__logging_02():
    import logging
    from rNotecards.logger import Logger
    from rNotecards.constants import PROJECT_ROOT_DIR

    log_file_full_path = PROJECT_ROOT_DIR / 'tests' / 'log' / 'app_02.log'
    log_level_file = getattr(logging, 'INFO')
    log_level_console = getattr(logging, 'INFO')

    test_logger_01 = Logger.setup_logger(log_file_full_path, log_level_file, log_level_console)
    test_logger_01.error('THIS IS AN ERROR')
    test_logger_01.warning('THIS IS AN WARNING')
    test_logger_01.info('THIS IS INFO')
    test_logger_01.debug('THIS IS A LOT OF INFO')

    # Read log file and split into lines
    with open(log_file_full_path, "r") as f:
        log_lines = f.read().splitlines()

    # Check that each log message appears in the log file
    assert 'THIS IS AN ERROR' in log_lines[-3]
    assert 'THIS IS AN WARNING' in log_lines[-2]
    assert 'THIS IS INFO' in log_lines[-1]
