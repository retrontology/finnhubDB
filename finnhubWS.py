import websocket
from threading import Thread
import json
import logging
import finnhub
import time

class finnhubWS():

    logger = logging.getLogger('finnhubWS')
    _ws_url = "wss://ws.finnhub.io?token="

    def __init__(self, token, trace=False):
        self.token = token
        self._trace = trace
        self._subscriptions = set()
        self._subscriptions_news = set()
        self._ws_thread = None
        self._open = False
        self.client = finnhub.Client(api_key=self.token)
        self.open()
    
    def __del__(self):
        self.close()

    def _open_loop(self):
        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                self.logger.error(e)

    def open(self):
        if not self._open:
            websocket.enableTrace(self._trace)
            self._ws = websocket.WebSocketApp(
                self._ws_url + self.token,
                on_message = self._on_message,
                on_error = self._on_error,
                on_close = self._on_close
                )
            self._ws.on_open = self._on_open
            self._ws_thread = Thread(target=self._open_loop)
            self._ws_thread.start()
            while not self._open: time.sleep(0.01)
            if self._subscriptions:
                for subscription in self._subscriptions:
                    self.subscribe(subscription)
            if self._subscriptions_news:
                for subscription in self._subscriptions_news:
                    self.subscribe_news(subscription)
        else:
            raise SocketAlreadyOpen
    
    def close(self):
        if self._open:
            self._ws.close()
            self._ws.keep_running = False
            self._ws_thread.join()
            self._ws_thread = None
        else:
            raise SocketAlreadyClosed
    
    def unsubscribe(self, symbol:str):
        symbol=symbol.upper()
        if symbol in self._subscriptions:
            try:
                request = {
                    'type': 'unsubscribe',
                    'symbol': symbol
                }
                self._ws.send(json.dumps(request))
            except Exception as e:
                self.logger.error(e)
            finally:
                self._subscriptions.remove(symbol)
        else:
            raise SubscriptionDoesNotExist
    
    def unsubscribe_news(self, symbol:str):
        symbol=symbol.upper()
        if symbol in self._subscriptions_news:
            try:
                request = {
                    'type': 'unsubscribe-news',
                    'symbol': symbol
                }
                self._ws.send(json.dumps(request))
            except Exception as e:
                self.logger.error(e)
            finally:
                self._subscriptions_news.remove(symbol)
        else:
            raise SubscriptionDoesNotExist
    
    def subscribe(self, symbol:str):
        symbol=symbol.upper()
        if not symbol in self._subscriptions:
            try:
                request = {
                    'type': 'subscribe',
                    'symbol': symbol
                }
                self._ws.send(json.dumps(request))
            except Exception as e:
                self.logger.error(e)
            finally:
                self._subscriptions.add(symbol)
        else:
            raise SubscriptionExists
    
    def subscribe_news(self, symbol:str):
        symbol=symbol.upper()
        if not symbol in self._subscriptions_news:
            try:
                request = {
                    'type': 'subscribe-news',
                    'symbol': symbol
                }
                self._ws.send(json.dumps(request))
            except Exception as e:
                self.logger.error(e)
            finally:
                self._subscriptions_news.add(symbol)
        else:
            raise SubscriptionExists

    # Meant to be overridden
    def trade_callback(self, symbol, price, timestamp, volume, conditions):
        pass

    # Meant to be overridden
    def news_callback(self, category, timestamp, headline, newsID, thumbnail_url, related, source, summary, url):
        pass

    # Meant to be overridden
    def on_open(self):
        pass

    # Meant to be overridden
    def on_close(self):
        pass

    # Meant to be overridden
    def on_error(self, error):
        pass
    
    def _parse_trades(self, message):
        self.logger.debug(f'Parsing trades from message data')
        for trade in message['data']:
            if 'c' in trade:
                conditions = trade['c']
            else:
                conditions = []
            self.trade_callback(
                trade['s'],
                trade['p'],
                trade['t'],
                trade['v'],
                conditions
                )

    def _parse_news(self, message):
        self.logger.debug(f'Parsing news from message data')
        for trade in message['data']:
            self.logger.debug(f'')
            self.news_callback(
                trade['category'],
                trade['datetime'],
                trade['headline'],
                trade['urlId'],
                trade['image'],
                trade['related'],
                trade['source'],
                trade['summary'],
                trade['url']
            )

    def _on_message(self, ws, message):
        self.logger.debug(f'Received message: {message}')
        message = json.loads(message)
        match message['type']:
            case 'trade':
                try:
                    self._parse_trades(message)
                except Exception as e:
                    self.logger.error(e)
            case 'news':
                try:
                    self._parse_news(message)
                except Exception as e:
                    self.logger.error(e)
            case 'ping':
                self.logger.debug(f'Received ping')
            case _:
                self.logger.error(f'Could not parse message for type: {message["type"]}')

    def _on_error(self, ws, error):
        self.logger.error(error)
        self.on_error(error)

    def _on_close(self, ws, status, message):
        self.logger.info(f'Websocket closed with status {status}: {message}')
        self._open = False
        self.on_close()

    def _on_open(self, ws):
        self.logger.info("Websocket opened")
        self._open = True
        self.on_open()



class SubscriptionExists(Exception): pass

class SubscriptionDoesNotExist(Exception): pass

class SocketAlreadyClosed(Exception): pass

class SocketAlreadyOpen(Exception): pass