import os
import io
import ftplib

from openpyxl import load_workbook

from returns.result import safe

SUCCESS_DIR = "success"
FAILURE_DIR = "failure"


def get_ftp_client() -> ftplib.FTP:
    client = ftplib.FTP(
        host=os.getenv("FTP_HOST", ""),
        user=os.getenv("FTP_USER", ""),
        passwd=os.getenv("FTP_PWD", ""),
    )
    client.encoding = "utf-8"
    return client


def list_files(client: ftplib.FTP) -> list[str]:
    return [
        i for i in client.nlst() if i not in (SUCCESS_DIR, FAILURE_DIR) and ".xlsx" in i
    ]


def get_content(client: ftplib.FTP):
    @safe
    def _get(filename: str) -> io.BytesIO:
        output = io.BytesIO()
        client.retrbinary(f"RETR {filename}", output.write)
        return output

    return _get


@safe
def parse_data(output: io.BytesIO) -> list[str]:
    output.seek(0)
    return [
        i.value
        for i in load_workbook(output, data_only=True)["Sheet1"]["G"][3:]
        if i.value
    ]


def _move_to_dir(dir_: str):
    def _move(client: ftplib.FTP, filename: str):
        @safe
        def __move(*args) -> str:
            client.rename(filename, f"{dir_}/{filename}")
            return filename

        return __move

    return _move


move_to_success = _move_to_dir(SUCCESS_DIR)
move_to_failure = _move_to_dir(FAILURE_DIR)
