from datetime import datetime
import uuid
import logging
from logging import handlers
import os, sys


# 日志模块
def logout(logName, *args):

    # 获取当前时间
    dt = datetime.now()

    try:
        # log文件
        save_path = os.getcwd() # 获取当前工作路径
        print(save_path)
        os.makedirs(save_path, exist_ok=True)
        log_file = '{}/log/{}-{}.log'.format(save_path, logName, dt.strftime('%Y-%m-%d'))

        logger = logging.getLogger('Debug{}'.format(uuid.uuid1()))
        logger.setLevel(logging.DEBUG)
        f_handler = handlers.TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7,
                                                      encoding="utf-8")
        f_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(processName)s[%(process)d]  - %(message)s"))

        # 输出到控制台
        sh_handler = logging.StreamHandler(sys.stdout)
        sh_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - pid[%(process)d] - %(levelname)s - %(message)s"))

        logger.addHandler(f_handler)
        logger.addHandler(sh_handler)

        if isinstance(args, tuple):
            logger.debug(' '.join(args))
        else:
            logger.debug('{}'.format(*args))
    except Exception:
        print("{} {}".format(dt.strftime('[%Y-%m-%d %H:%M:%S %f]'), *args))

    finally:
        logger.removeHandler(f_handler)
        logger.removeHandler(sh_handler)