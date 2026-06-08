import logging

def setup_logging():
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler()
        ]
    )

def validate_inputs(symbol: str, side: str, order_type: str, quantity: float, price: float = None):
    if not symbol.upper().endswith("USDT"):
        raise ValueError("Symbol must be a USDT pair, e.g., BTCUSDT.")

    if order_type.upper() not in ["MARKET", "LIMIT"]:
        raise ValueError("Order type must be either 'MARKET' or 'LIMIT'.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than 0.")

    if order_type.upper() == "LIMIT" and (price is None or price <= 0):
        raise ValueError("Price must be greater than 0 for LIMIT orders.")

    if side.upper() not in ["BUY", "SELL"]:
        raise ValueError("Side must be either 'BUY' or 'SELL'.")
import time
import hmac
import hashlib
import requests
import logging
from decimal import Decimal, ROUND_DOWN

class BinanceFuturesTestnetClient:
    def __init__(self, api_key: str, api_secret: str):
        self.base_url = "https://testnet.binancefuture.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange_info = None
        self.logger = logging.getLogger(__name__)
        self._load_exchange_info()

    def _adjust_price(self, price: float, tick_size: Decimal, min_price: Decimal) -> str:
        p = Decimal(str(price))
        if p < min_price:
            raise ValueError(f"Price {p} below minPrice {min_price}")
        precision = abs(tick_size.as_tuple().exponent)
        adjusted = (p / tick_size).quantize(Decimal('1'), rounding=ROUND_DOWN) * tick_size
        return f"{adjusted:.{precision}f}".rstrip('0').rstrip('.')

    def _adjust_quantity(self, quantity: float, step_size: Decimal, min_qty: Decimal) -> str:
        q = Decimal(str(quantity))
        if q < min_qty:
            raise ValueError(f"Quantity {q} below minQty {min_qty}")
        precision = abs(step_size.as_tuple().exponent)
        adjusted = (q // step_size) * step_size
        return f"{adjusted:.{precision}f}".rstrip('0').rstrip('.')

    def _generate_signature(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _get_symbol_filters(self, symbol: str):
        if not self.exchange_info:
            raise RuntimeError("ExchangeInfo not loaded")
        symbol = symbol.upper()
        for s in self.exchange_info['symbols']:
            if s['symbol'] == symbol:
                filters = {f['filterType']: f for f in s['filters']}
                return {
                    'minNotional': Decimal(filters['MIN_NOTIONAL']['notional']),
                    'minQty': Decimal(filters['LOT_SIZE']['minQty']),
                    'minPrice': Decimal(filters['PRICE_FILTER']['minPrice']),
                    'stepSize': Decimal(filters['LOT_SIZE']['stepSize']),
                    'tickSize': Decimal(filters['PRICE_FILTER']['tickSize'])
                }
        raise ValueError(f"Symbol {symbol} not found in exchangeInfo")

    def _load_exchange_info(self):
        url = f"{self.base_url}/fapi/v1/exchangeInfo"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            self.exchange_info = resp.json()
            self.logger.info("Loaded exchangeInfo successfully")
        except Exception as e:
            self.logger.error(f"Failed to load exchangeInfo: {e}")
            raise

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        endpoint = "/fapi/v1/order"
        url = f"{self.base_url}{endpoint}"
        timestamp = int(time.time() * 1000)
        
        try:
            filters = self._get_symbol_filters(symbol)
        except Exception as e:
            self.logger.error(f"Filter error: {e}")
            return {"error": True, "message": str(e)}

        try:
            adj_quantity = self._adjust_quantity(quantity, filters['stepSize'], filters['minQty'])
        except ValueError as e:
            self.logger.error(f"Quantity error: {e}")
            return {"error": True, "message": str(e)}

        params = {
            "quantity": adj_quantity,
            "recvWindow": 5000,
            "side": side.upper(),
            "symbol": symbol.upper(),
            "timestamp": timestamp,
            "type": order_type.upper()
        }
        
        if order_type.upper() == "LIMIT":
            if price is None:
                return {"error": True, "message": "Price required for LIMIT orders"}
            try:
                adj_price = self._adjust_price(price, filters['tickSize'], filters['minPrice'])
                params["price"] = adj_price
                params["timeInForce"] = "GTC"
                notional = Decimal(adj_quantity) * Decimal(adj_price)
                if notional < filters['minNotional']:
                    msg = f"Notional {notional} < minNotional {filters['minNotional']}"
                    self.logger.error(msg)
                    return {"error": True, "message": msg}
            except ValueError as e:
                self.logger.error(f"Price error: {e}")
                return {"error": True, "message": str(e)}

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = self._generate_signature(query_string)
        query_string += f"&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        self.logger.info(f"Sending Order Request: {params}")

        try:
            response = requests.post(url, data=query_string, headers=headers, timeout=10)
            response_json = response.json()
            if response.status_code == 200:
                self.logger.info(f"SUCCESS: Order executed. Response: {response_json}")
                return response_json
            else:
                self.logger.error(f"API ERROR {response.status_code}: {response_json}")
                return {"error": True, "message": response_json.get("msg", "Unknown API error")}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"NETWORK ERROR: {e}")
            return {"error": True, "message": f"Network exception: {str(e)}"}
        import argparse
import os


load_dotenv()

def main():
    setup_logging()
    
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        print("[CRITICAL ERROR] Missing API Keys! Set BINANCE_API_KEY and BINANCE_API_SECRET in .env")
        return

    parser = argparse.ArgumentParser(description="Binance Futures Testnet Trading Bot")
    parser.add_argument("--price", type=float, help="Required if type is LIMIT")
    parser.add_argument("--quantity", type=float, required=True)
    parser.add_argument("--side", type=str, required=True, choices=["BUY", "SELL"])
    parser.add_argument("--symbol", type=str, required=True, help="Trading pair, e.g., BTCUSDT")
    parser.add_argument("--type", type=str, required=True, choices=["MARKET", "LIMIT"])

    args = parser.parse_args()

    try:
        validate_inputs(args.symbol, args.side, args.type, args.quantity, args.price)
    except ValueError as err:
        print(f"[INPUT ERROR] {err}")
        return

    print("\n--- ORDER REQUEST SUMMARY ---")
    print(f"Price:     {args.price}")
    print(f"Quantity:  {args.quantity}")
    print(f"Side:      {args.side.upper()}")
    print(f"Symbol:    {args.symbol.upper()}")
    print(f"Type:      {args.type.upper()}")
    print("-----------------------------\n")
   
    client = BinanceFuturesTestnetClient(api_key, api_secret)
    result = client.place_order(
        symbol=args.symbol,
        side=args.side,
        order_type=args.type,
        quantity=args.quantity,
        price=args.price
    )

    print("\n--- ORDER RESPONSE DETAILS ---")
    if result.get("error"):
        print(f"Message: {result['message']}")
        print(f"Status: FAILURE")
    else:
        print(f"Avg Price: {result.get('avgPrice', 'N/A')}")
        print(f"Executed Qty: {result.get('executedQty')}")
        print(f"Order ID: {result.get('orderId')}")
        print(f"Status: SUCCESS ({result.get('status')})")
    print("------------------------------\n")

if __name__ == "__main__":
    main()
