
import sys
print(sys.executable)
print(sys.version)
import argparse
import os

from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.orders import OrderManager
from bot.validators import (
    validate_side,
    validate_order_type,
    validate_quantity
)

load_dotenv()

API_KEY = os.getenv(
    "BINANCE_API_KEY"
)

API_SECRET = os.getenv(
    "BINANCE_API_SECRET"
)

BASE_URL = os.getenv(
    "BASE_URL"
)

def main():

    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot"
    )

    parser.add_argument(
        "--symbol",
        required=True
    )

    parser.add_argument(
        "--side",
        required=True
    )

    parser.add_argument(
        "--type",
        required=True
    )

    parser.add_argument(
        "--quantity",
        required=True,
        type=float
    )

    parser.add_argument(
        "--price",
        type=float
    )

    args = parser.parse_args()

    side = validate_side(args.side)

    order_type = validate_order_type(
        args.type
    )

    quantity = validate_quantity(
        args.quantity
    )

    if (
        order_type == "LIMIT"
        and args.price is None
    ):
        raise ValueError(
            "LIMIT order requires --price"
        )

    client = BinanceClient(
        API_KEY,
        API_SECRET,
        BASE_URL
    )

    manager = OrderManager(client)

    print("\nOrder Request Summary")
    print("----------------------")
    print(f"Symbol: {args.symbol}")
    print(f"Side: {side}")
    print(f"Type: {order_type}")
    print(f"Quantity: {quantity}")

    if args.price:
        print(f"Price: {args.price}")

    response = manager.place_order(
        symbol=args.symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=args.price
    )

    print("\nOrder Response")
    print("----------------------")

    print(
        f"Order ID: {response.get('orderId')}"
    )

    print(
        f"Status: {response.get('status')}"
    )

    print(
        f"Executed Qty: {response.get('executedQty')}"
    )

    print(
        f"Average Price: {response.get('avgPrice')}"
    )

    print(
        "\nOrder placed successfully."
    )


if __name__ == "__main__":
    main()
    