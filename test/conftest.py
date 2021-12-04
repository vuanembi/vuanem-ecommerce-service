import requests
import pytest

from libs.restlet import netsuite_session

@pytest.fixture()
def session():
    return requests.Session()


@pytest.fixture()
def oauth_session():
    return netsuite_session()
    
