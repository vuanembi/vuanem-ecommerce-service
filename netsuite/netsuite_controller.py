from netsuite.saved_search_service import coupon_code_ss_service

services = {
    "/netsuite/saved_search/coupon_code": coupon_code_ss_service,
}


def netsuite_controller(request) -> dict:
    if request.path in services:
        return services[request.path](request.get_json()).unwrap()
    else:
        return {
            "status": 200,
        }
