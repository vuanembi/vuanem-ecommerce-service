from lazada import lazada_service


def lazada_controller(request_data: dict) -> dict:
    return (
        lazada_service.get_orders_service()
        .bind(lazada_service.order_service)
        .map(lambda x: {"controller": "lazada", "results": x})
        .unwrap()
    )
