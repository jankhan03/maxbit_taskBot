import logging

'''В этом файле мы создадим базовые настройки логгирования, для использования в остальном проекте'''

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
