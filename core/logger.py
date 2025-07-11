import logging
from core.settings import DEBUG
logging.basicConfig(format='%(levelname)s - %(asctime)s, %(pathname)s:%(lineno)d , message: %(message)s')
logger = logging.getLogger(__name__)

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

