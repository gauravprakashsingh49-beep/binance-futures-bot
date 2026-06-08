from bot logging_config import setup_logger

logger = setup_logger()

class OrderManager:

    def __init__(self, client):
        self.client = client

    def place_order(
        self,
        symbol,
        side,
        order_type,
        quantity,
        price=None
    ):

        payload = {
            "symbol": symbol.upper(),
            "side": side,
            "type": order_type,
            "quantity": quantity
        }

        if order_type == "LIMIT":

            payload["price"] = price
            payload["timeInForce"] = "GTC"

        logger.info(
            f"Request: {payload}"
        )

        try:

            response = self.client.place_order(
                payload
            )

            logger.info(
                f"Response: {response}"
            )

            return response

        except Exception as e:

            logger.exception(
                f"Order failed: {e}"
            )

            raise