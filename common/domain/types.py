from decimal import Decimal
from typing import TypedDict


class OrderDict(TypedDict):
    id: int
    client_id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    total_value: Decimal
    delivery_date: str
    status: str


class OfferDict(TypedDict):
    id: int
    product_id: int
    cooperated_id: int
    quantity: Decimal
    start_date: str
    end_date: str
    status: str


class DistributionDict(TypedDict):
    id: int
    offer_id: int
    order_id: int
    cooperated_id: int
    quantity: Decimal
    total_value: Decimal
