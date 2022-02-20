from datetime import date

from returns.result import Success, ResultE
from returns.pipeline import flow
from returns.pointfree import lash

from netsuite.query import query_repo
from netsuite.query.analytics import analytics
from netsuite.restlet import restlet, restlet_repo


def coupon_code_service(data: dict[str, list[str]]) -> ResultE[dict[str, list[str]]]:
    with restlet_repo.netsuite_session() as session:
        return flow(
            data["data"],
            lambda values: {
                "id": analytics.Dataset.CouponCode.value,
                "cond": [
                    {
                        "fieldId": "code",
                        "operator": "ANY_OF",
                        "values": values,
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
            },
            query_repo.request(session, restlet.Analytics),
            lash(lambda _: Success({"data": []})),  # type: ignore
        )
