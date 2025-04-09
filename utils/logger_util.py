# logger_config.py
import logging

def setup_logger(name, probset_dir=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    if probset_dir is not None:
        fh = logging.FileHandler(f'{probset_dir}/{name}.log')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    
    logger.addHandler(ch)
    return logger

logger = setup_logger('AutoEval')