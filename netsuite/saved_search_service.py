from typing import Any

from returns.result import Result, ResultE, Success
from returns.methods import cond

from netsuite import restlet, restlet_repo, saved_search_repo

get_coupon_code_ss = saved_search_repo.get_saved_search(restlet.CouponCodeSS)


def coupon_code_ss_service(request_data: dict) -> ResultE[dict[str, Any]]:
    with restlet_repo.netsuite_session() as session:
        return (
            cond(
                Result,
                "data" in request_data and isinstance(request_data["data"], list),
                request_data,
                request_data,
            )
            .map(lambda x: x["data"])
            .map(lambda x: ",".join(x))
            .bind(
                lambda x: get_coupon_code_ss(session)(
                    {
                        "col": "code",
                        "values": x,
                    }
                )
            )
            .lash(lambda _: Success({"data": []}))
        )
