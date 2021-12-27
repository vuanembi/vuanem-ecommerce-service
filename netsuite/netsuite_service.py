from returns.pipeline import flow
from returns.pointfree import bind, lash

from netsuite import netsuite_repo, prepare_repo, restlet_repo

def create_order_service(prepared_id):
    with restlet_repo.netsuite_session() as session:
        return flow(
            prepared_id,
            prepare_repo.get_prepared_order(prepared_id),
            bind(prepare_repo.validate_prepared_order("pending")),
            bind(netsuite_repo.build_sales_order_from_prepared(session)),
            bind(netsuite_repo.create_sales_order(session))
        )
