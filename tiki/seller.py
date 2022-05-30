from netsuite.sales_order import sales_order, sales_order_service
from netsuite.customer import customer, customer_repo
from netsuite.location import location

from common.seller import Seller

TIKI = Seller(
    name="Tiki",
    order_builder=sales_order_service.build(
        items_fn=lambda x: x["items"],
        item_sku_fn=lambda x: x["product"]["seller_product_code"],
        item_qty_fn=lambda x: x["seller_income_detail"]["item_qty"],
        item_amt_fn=lambda x: (
            x["seller_income_detail"]["item_price"]
            * x["seller_income_detail"]["item_qty"]
        )
        - x["seller_income_detail"]["discount"]["discount_coupon"]["seller_discount"]
        if x["_fulfillment_type"] == "tiki_delivery"
        else x["seller_income_detail"]["sub_total"],
        ecom=sales_order.Ecommerce(
            subsidiary=location.SUBSIDIARY,
            department=location.DEPARTMENT,
            location=788,
            custbody_order_payment_method=23,
            salesrep=1664,
            partner=916906,
            custbody_onl_rep=942960,
        ),
        memo_builder=lambda x: f"{x['code']} - tiki",
        customer_builder=lambda x: customer_repo.add(  # type: ignore
            customer.Customer(
                entity=None,
                custbody_customer_phone="1998103102",
                custbody_recipient_phone="1998103102",
                custbody_recipient="TEMP Tiki",
                shippingaddress={
                    "addressee": "TEMP Tiki",
                    "custrecord_cityprovince": 66,
                    "custrecord_districts": 1,
                },
                shipaddress=customer.ROOT_ADDRESS,
            ),
            x["shipping"]["address"]["phone"],
            x["shipping"]["address"]["full_name"][:30],
            customer_repo.add_shipping_address(
                [
                    x["shipping"]["address"].get("full_name"),
                    x["shipping"]["address"].get("street", "Phố X"),
                    x["shipping"]["address"].get("ward", "Phường X"),
                    x["shipping"]["address"].get("district", "Quận X"),
                    x["shipping"]["address"].get("region", "Tỉnh X"),
                    x["shipping"]["address"].get("country", "X"),
                ]
            ),
        ),
    ),
    chat_id="-1001685563275",
)
