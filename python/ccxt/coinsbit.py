# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
import base64
import hashlib
import math
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import ArgumentsRequired
from ccxt.base.errors import OrderNotFound


class coinsbit (Exchange):

    def describe(self):
        return self.deep_extend(super(coinsbit, self).describe(), {
            'id': 'coinsbit',
            'name': 'Coinsbit',
            'countries': ['EE'],
            'version': 'v1',
            'rateLimit': 1000,
            'has': {
                'createMarketOrder': False,
                'fetchOrder': True,
                'fetchOrders': True,
                'fetchCurrencies': False,
                'fetchTicker': False,
                'fetchTickers': False,
                'fetchOHLCV': False,
                'fetchTrades': False,
            },
            'urls': {
                'api': {
                    'public': 'https://coinsbit.io/api/v1/public',
                    'private': 'https://coinsbit.io/api/v1',
                    'wapi': 'wss://coinsbit.io/api/v1/trade_ws',
                },
                'www': 'https://coinsbit.io/',
                'doc': [
                    'https://www.notion.so/API-COINSBIT-WS-API-COINSBIT-cf1044cff30646d49a0bab0e28f27a87',
                ],
                'fees': 'https://coinsbit.io/fee-schedule',
            },
            'api': {
                'public': {
                    'get': [
                        'markets',
                        'tickers',
                        'ticker',
                        'book',
                        'history',
                        'symbols',
                        'depth/result',
                    ],
                    'post': [
                        'order/new',
                        'order/cancel',
                        'orders',
                        'account/balances',
                        'account/balance',
                        'account/order',
                        'account/order_history',
                    ],
                },
                'private': {
                    'get': [
                        'markets',
                        'tickers',
                        'ticker',
                        'book',
                        'history',
                        'symbols',
                        'depth/result',
                    ],
                    'post': [
                        'order/new',
                        'order/cancel',
                        'orders',
                        'account/balances',
                        'account/balance',
                        'account/order',
                        'account/order_history',
                    ],
                },
                'wapi': {
                    'server': [
                        'ping',
                        'time',
                    ],
                    'kline': [
                        'subscribe',
                        'unsubscribe',
                    ],
                    'price': [
                        'subscribe',
                        'unsubscribe',
                    ],
                    'state': [
                        'query',
                        'subscribe',
                        'unsubscribe',
                    ],
                    'deals': [
                        'subscribe',
                        'unsubscribe',
                    ],
                    'depth': [
                        'subscribe',
                        'unsubscribe',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.002,
                    'taker': 0.002,
                },
                'funding': {
                    'withdraw': {
                        'BTC': 0.0,
                        'ETH': 0.0,
                        'KSH': 0.0,
                    },
                },
            },
        })

    def fetch_markets(self, params={}):
        response = self.publicGetMarkets(params)
        markets = self.safe_value(response, 'result')
        numMarkets = len(markets)
        if numMarkets < 1:
            raise ExchangeError(self.id + ' publicGetMarkets returned empty response: ' + self.json(markets))
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            baseId = self.safe_string(market, 'stock')
            quoteId = self.safe_string(market, 'money')
            id = baseId + '_' + quoteId
            base = self.safe_currency_code(baseId)
            quote = self.safe_currency_code(quoteId)
            symbol = base + '/' + quote
            precision = {
                'amount': market['stockPrec'],
                'price': market['moneyPrec'],
            }
            minAmount = self.safe_float(market, 'minAmount', 0)
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': True,
                'precision': precision,
                'limits': {
                    'amount': {
                        'min': minAmount,
                        'max': None,
                    },
                    'price': {
                        'min': math.pow(10, -precision['price']),
                        'max': None,
                    },
                    'cost': {
                        'min': -1 * math.log10(precision['amount']),
                        'max': None,
                    },
                },
                'info': market,
            })
        return result

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        method = 'privatePostOrderNew'
        request = {
            'pair': market['id'],
            'amount': self.amount_to_precision(symbol, amount),
            'price': self.price_to_precision(symbol, price),
        }
        response = getattr(self, method)(self.extend(request, params))
        order = self.parse_order(response, market)
        return self.extend(order, {
            'type': type,
        })

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        request = {
            'market': self.market_id(symbol),
            'order_id': int(id),
        }
        return self.privatePostOrderCancel(self.extend(request, params))

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchOrders requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
        }
        if limit is not None:
            request['limit'] = limit
        response = self.privatePostOrders(self.extend(request, params))
        result = response.result
        return self.parse_orders(result, market, since, limit)

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        orderIdField = self.get_order_id_field()
        request = {}
        request[orderIdField] = id
        response = self.privatePostAccountOrder(self.extend(request, params))
        if len(response['result']) == 0:
            raise OrderNotFound(self.id + ' order ' + id + ' not found')
        return self.parse_order(response['result']['records'])

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        request = {
            'market': self.market_id(symbol),
        }
        if limit is not None:
            request['limit'] = limit
        response = self.publicGetDepthResult(self.extend(request, params))
        return self.parse_order_book(response, None, 'bids', 'asks')

    def fetch_balance(self, params={}):
        self.load_markets()
        query = self.omit(params, 'type')
        response = self.privatePostAccountBalances(query)
        balances = self.safe_value(response, 'result')
        symbols = list(balances.keys())
        result = {'info': balances}
        for i in range(0, len(symbols)):
            currencyId = symbols[i]
            code = self.safe_currency_code(currencyId)
            balance = balances[code]
            account = self.account()
            account['free'] = self.safe_float(balance, 'available')
            account['total'] = self.safe_float(balance, 'available') + self.safe_float(balance, 'freeze')
            result[code] = account
        return self.parse_balance(result)

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            request = '/api/' + self.version + '/' + self.implode_params(path, params)
            nonce = str(self.nonce())
            query = self.extend({
                'nonce': str(nonce),
                'request': request,
            }, query)
            body = self.json(query)
            query = self.encode(body)
            payload = base64.b64encode(query)
            secret = self.encode(self.secret)
            signature = self.hmac(payload, secret, hashlib.sha512)
            headers = {
                'Content-type': 'application/json',
                'X-TXC-APIKEY': self.apiKey,
                'X-TXC-PAYLOAD': payload,
                'X-TXC-SIGNATURE': signature,
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def parse_order(self, order, market=None):
        marketName = self.safe_string(order, 'market')
        market = market or self.find_market(marketName)
        symbol = self.safe_string(market, 'symbol')
        timestamp = self.safe_string(order, 'time')
        if timestamp is not None:
            timestamp = int(timestamp) * 1000
        amount = self.safe_float(order, 'amount')
        fillAmount = self.safe_float(order, 'dealStock', amount)
        remaining = amount - fillAmount
        return {
            'id': self.safe_string(order, 'id'),
            'datetime': self.iso8601(timestamp),
            'timestamp': timestamp,
            'lastTradeTimestamp': None,
            'status': None,
            'symbol': symbol,
            'type': self.safe_string(order, 'type'),
            'side': self.safe_string(order, 'side'),
            'price': self.safe_float(order, 'price'),
            'cost': self.safe_float(order, 'dealFee', 0.0) + self.safe_float(order, 'takerFee', 0.0),
            'amount': amount,
            'filled': fillAmount,
            'remaining': remaining,
            'fee': self.safe_float(order, 'fee'),
            'info': order,
        }

    def get_order_id_field(self):
        return 'orderId'
