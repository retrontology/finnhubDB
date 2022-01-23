from finnhubWS import finnhubWS
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

class finnhubLiveDB(finnhubWS):

    def __init__(self, influx_ip, influx_port, influx_org, influx_bucket, influx_token, finnhub_token):
        self.influx_ip = influx_ip
        self.influx_port = influx_port
        self.influx_org = influx_org
        self.influx_bucket = influx_bucket
        self.influx_token = influx_token
        self.influx_client = influxdb_client.InfluxDBClient(
            url=f'http://{influx_ip}:{influx_port}', 
            token=influx_token, 
            org=influx_org
            )
        self.influx_write = self.influx_client.write_api(write_options=ASYNCHRONOUS)
        super().__init__(finnhub_token)
    
    def trade_callback(self, symbol, price, timestamp, volume, conditions):
        p = influxdb_client.Point('trade').tag("symbol", symbol).field('price', price).field('volume', volume).time(timestamp, write_precision=influxdb_client.WritePrecision.MS)
        self.influx_write.write(bucket=self.influx_bucket, record=p)

    def news_callback(self, category, timestamp, headline, newsID, thumbnail_url, related, source, summary, url):
        pass

    def on_open(self):
        pass

    def on_close(self):
        pass

    def on_error(self, error):
        pass