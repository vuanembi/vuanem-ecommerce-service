import requests
from returns.result import ResultE
from returns.functions import raise_exception

from common import utils
from lazada import lazada, auth_repo, lazada_repo


def _update_new_token(session: requests.Session):
    def _update(token: lazada.AccessToken) -> ResultE[lazada.AccessToken]:
        return (
            auth_repo.refresh_token(session, token)
            .bind(auth_repo.update_access_token)
            .lash(raise_exception)
        )

    return _update


def auth_service(session: requests.Session) -> ResultE[lazada.AccessToken]:
    return (
        auth_repo.get_access_token()
        .bind(utils.check_expired)  # type: ignore
        .lash(_update_new_token(session))
    )
