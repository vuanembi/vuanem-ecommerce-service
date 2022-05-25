from dataclasses import dataclass, field

from google.cloud.firestore import DocumentReference

from netsuite.sales_order.sales_order_service import OrderBuilder
from db.firestore import DB
from telegram.message_service import get_chat_id


@dataclass()
class Seller:
    name: str
    order_builder: OrderBuilder
    chat_id: str
    db: DocumentReference = field(init=False)

    def __post_init__(self):
        self.db = DB.document(self.name)
        self.chat_id = get_chat_id(self.chat_id)
