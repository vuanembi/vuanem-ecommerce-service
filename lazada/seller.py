from netsuite.sales_order import sales_order, sales_order_service
from netsuite.customer import customer, customer_repo
from netsuite.location import location

from common.seller import Seller

_lazada_seller = lambda name, location_, chat_id: Seller(
    name=name,
    order_builder=sales_order_service.build(
        items_fn=lambda x: x["items"],
        item_sku_fn=lambda x: x["sku"],
        item_qty_fn=lambda _: 1,
        item_amt_fn=lambda x: x["paid_price"] + x["voucher_platform"],
        ecom=sales_order.Ecommerce(
            subsidiary=location.SUBSIDIARY,
            department=location.DEPARTMENT,
            location=location_,
            custbody_order_payment_method=44,
            salesrep=1664,
            partner=923414,
            custbody_onl_rep=722312,
        ),
        memo_builder=lambda x: f"{x['order_id']} - lazada",
        customer_builder=lambda _: customer_repo.add(
            customer.Customer(
                entity=None,
                custbody_customer_phone="1998103103",
                custbody_recipient_phone="1998103103",
                custbody_recipient="TEMP Lazada",
                shippingaddress={
                    "addressee": "TEMP Lazada",
                },
                shipaddress=customer.ROOT_ADDRESS,
            )
        ),
    ),
    chat_id=chat_id,
)

SELLERS = {
    i.name: i
    for i in [
        _lazada_seller("Lazada", 789, "-661578343"),
        _lazada_seller("Lazada2", 862, "-770270636"),
    ]
}
