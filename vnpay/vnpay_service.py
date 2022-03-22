import ftplib

from returns.pointfree import bind, lash
from returns.pipeline import flow

from vnpay import vnpay_repo


def match_service(client: ftplib.FTP, filename: str):
    return flow(
        filename,
        vnpay_repo.get_content(client),
        bind(vnpay_repo.parse_data),
        bind(vnpay_repo.move_to_success(client, filename)),
        lash(vnpay_repo.move_to_failure(client, filename)),
    )


def pipeline():
    with vnpay_repo.get_ftp_client() as client:
        return [match_service(client, i) for i in vnpay_repo.list_files(client)]
