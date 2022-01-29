import logging
from finnhubLiveDB import finnhubLiveDB

FINNHUB_API_KEY = 'FINNHUB_API_KEY'
FINNHUB_SANDBOX_API_KEY = 'FINNHUB_SANDBOX_API_KEY'
FINNHUB_WEBHOOK_SECRET = 'FINNHUB_WEBHOOK_SECRET'

INFLUXDB_USER = 'INFLUXDB_USER'
INFLUXDB_PASS = 'INFLUXDB_PASS'
INFLUXDB_TOKEN = 'INFLUXDB_TOKEN'
INFLUXDB_BUCKET = 'INFLUXDB_BUCKET'
INFLUXDB_IP = 'INFLUXDB_IP'
INFLUXDB_ORG = 'INFLUXDB_ORG'
INFLUXDB_PORT = 8086

CRYPTO_SYMBOLS = [
    'COINBASE:BTC-USD',
    'COINBASE:ETH-USD',
    'COINBASE:DOGE-USD',
    'COINBASE:USDT-USD',
    'COINBASE:ADA-USD'
]

def main():
    setup_logger(debug=True)
    db = finnhubLiveDB(INFLUXDB_IP, INFLUXDB_PORT, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN, FINNHUB_API_KEY)
    for symbol in CRYPTO_SYMBOLS:
        db.subscribe(symbol)

def setup_logger(debug=False):
    logger = logging.getLogger()
    stream_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)
    file_handler = logging.FileHandler('finnhubDB.log')
    file_handler.setFormatter(stream_formatter)
    if debug:
        logger.setLevel(logging.DEBUG)
        stream_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        stream_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger

if __name__ == '__main__':
    main()