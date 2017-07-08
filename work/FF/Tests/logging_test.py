import logging,time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add the handlers to the logger
fh = logging.FileHandler("error.log")
fh.setLevel(logging.INFO)
logger.addHandler(fh)

while(True):
    try:
        open('/path/to/does/not/exist', 'rb')
    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception, e:
        logger.info('Failed to open file', exc_info=True)
