import logging
import os

logger = None


def logging_setup(level):
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    FORMAT = '%(asctime)s %(levelname)-s %(message)s'
    logging.basicConfig(format = FORMAT)


def read_secret(secret_argument, secret_type):
    if secret_argument == '-':
        return None
    secret = None
    match secret_type:
        case "plain":
            content = secret_argument
            secret = content.strip()
        case "env":
            if secret_argument not in os.environ:
                return None
            content = os.environ[secret_argument]
            secret = content.strip()
        case "file":
            if not os.access(secret_argument, os.R_OK):
                return None
            with open(secret_argument, "r") as f:
                content = f.read();
                secret = content.strip()
        case "_":
            logger.error(f"TODO implement! Unknown secret_type: {secret_type}")
            return
    return secret


def read_config(config, parameter):
    cfg = config
    params = parameter.split('.')
    for p in params:
        if cfg is None:
            return None
        if p not in cfg:
            return None
        cfg = cfg[p]
    return cfg


def read_config_secret(config, parameter):
    secret_type = read_config(config, 'secret_type')
    secret_argument = read_config(config, parameter)
    secret = read_secret(secret_argument, secret_type)
    return secret


def truncate( text, maxlen ):
    if len(text) < maxlen:
        return text
    idx = text.rfind(" ", 0, maxlen-3)
    return text[:idx] + "..."
