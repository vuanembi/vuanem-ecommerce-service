from typing import Any
from datetime import date

from returns.result import Result, ResultE, Success
from returns.methods import cond

from netsuite.analytics import analytics_repo
from netsuite.restlet import restlet, restlet_repo


def validation_service(
    request_data: dict[str, Any]
) -> Result[dict[str, Any], dict[str, Any]]:
    return cond(
        Result,
        "data" in request_data and isinstance(request_data["data"], list),
        request_data,
        request_data,
    )


def coupon_code_analytics_service(request_data: dict[str, list[str]]):
    with restlet_repo.netsuite_session() as session:
        return (
            validation_service(request_data)
            .map(lambda x: x["data"])
            .map(
                lambda codes: {
                    "id": restlet.Dataset.CouponCode.value,
                    "cond": [
                        {
                            "fieldId": "code",
                            "operator": "ANY_OF",
                            "values": codes,
                        },
                        {
                            "fieldId": "promotion.currency.currency",
                            "operator": "EQUAL",
                            "values": [1],
                        },
                        {
                            "fieldId": "promotion.usetype",
                            "operator": "ANY_OF",
                            "values": ["SINGLEUSE"],
                        },
                        {
                            "fieldId": "promotion.enddate",
                            "operator": "ON_OR_AFTER",
                            "values": [date.today().isoformat()],
                        },
                    ],
                }
            )
            .bind(analytics_repo.post_analytics(session))
            .lash(lambda _: Success({"data": []}))
        )


get_coupon_code_ss = analytics_repo.get_saved_search(restlet.CouponCodeSS)


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
