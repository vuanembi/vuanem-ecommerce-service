from typing import TypedDict, Protocol, Union

import requests


class RequestBuilder(Protocol):
    def __call__(
        self,
        uri: str,
        method: str,
        params: dict[str, Union[int, str]] = {},
        body: dict[str, Union[int, str]] = {},
    ) -> requests.PreparedRequest:
        pass


class AccessToken(TypedDict):
    access_token: str
    refresh_token: str


OrderSN = str


class Item(TypedDict):
    item_name: str
    item_sku: str
    model_quantity_purchased: int
    model_original_price: int
    model_discounted_price: int


class Order(TypedDict):
    order_sn: OrderSN
    create_time: int
    item_list: list[Item]
