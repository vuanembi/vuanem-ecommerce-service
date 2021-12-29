from tiki import tiki_service


def tiki_controller(request_data: dict) -> dict:
    with tiki_service.auth_service() as session:
        return (
            tiki_service.pull_service(session)
            .bind(tiki_service.events_service(session))
            .map(lambda x: {"controller": "tiki", "results": x})
        ).unwrap()
