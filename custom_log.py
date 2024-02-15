import logging
import os

def cust_log(file_name:str, path:str="./", level:str="info", main_level:str="debug"):
    '''
    Custom logging module that also print to screen all messages.

    Parameters
    ----------

        file_name : str
            log file name expressed with extension ( .log )
        path : str
            path to log file ( default = '.' )
        level : str 
            level of logging and file: INFO, DEBUG (default), ERROR
        level : str 
            level of console logging: INFO (default), DEBUG, ERROR
    '''
    def check_level(lev):
        if lev=="info":
            lvl=logging.INFO
        if lev=="debug":
            lvl=logging.DEBUG
        if lev=="error":
            lvl=logging.ERROR
        return lvl

    if not os.path.exists(path):
        os.makedirs(path)
    # logging.basicConfig(filename=path+file_name, format='%(asctime)s %(levelname)-8s %(message)s', level=lvl,datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger()
    logger.setLevel(check_level(main_level))
    fh = logging.FileHandler(path+file_name)
    fh.setLevel(check_level(main_level))
    ch = logging.StreamHandler()
    ch.setLevel(check_level(level))
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logging