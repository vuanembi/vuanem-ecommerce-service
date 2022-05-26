from netsuite.sales_order import sales_order, sales_order_service
from netsuite.customer import customer, customer_repo
from netsuite.location import location

from common.seller import Seller

_shopee_seller = lambda name, id_, location_, chat_id: Seller(
    name=name,
    order_builder=sales_order_service.build(
        items_fn=lambda x: x["item_list"],
        item_sku_fn=lambda x: x["item_sku"],
        item_qty_fn=lambda x: x["model_quantity_purchased"],
        item_amt_fn=lambda x: x["model_discounted_price"],
        ecom=sales_order.Ecommerce(
            subsidiary=location.SUBSIDIARY,
            department=location.DEPARTMENT,
            location=location_,
            custbody_order_payment_method=41,
            salesrep=1664,
            partner=915574,
            custbody_onl_rep=933725,
        ),
        memo_builder=lambda x: f"{x['order_sn']} - shopee",
        customer_builder=lambda _: customer_repo.add(
            customer.Customer(
                entity=None,
                custbody_customer_phone="1998103101",
                custbody_recipient_phone="1998103101",
                custbody_recipient="TEMP Shopee",
                shippingaddress={
                    "addressee": "TEMP Shopee",
                },
                shipaddress=customer.ROOT_ADDRESS,
            )
        ),
    ),
    chat_id=chat_id,
    id=id_,
)

SHOPEE = _shopee_seller("Shopee", 179124960, 789, "-628755636")
SHOPEE2 = _shopee_seller("Shopee2", 653870673, 882, "-694445118")
