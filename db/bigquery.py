from typing import Any
from datetime import datetime

from google.cloud import bigquery
from returns.result import safe

BQ_CLIENT = bigquery.Client()


def transform_data(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            **d,
            "_batched_at": datetime.utcnow().isoformat(timespec="seconds"),
        }
        for d in data
    ]


def transform_schema(schema: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return schema + [{"name": "_batched_at", "type": "TIMESTAMP"}]


def load(dataset: str, table: str, schema: list[dict[str, Any]]):
    @safe
    def _load(data: list[dict[str, Any]]) -> int:
        return (
            BQ_CLIENT.load_table_from_json(
                transform_data(data),
                f"{dataset}.{table}",
                job_config=bigquery.LoadJobConfig(
                    create_disposition="CREATE_IF_NEEDED",
                    write_disposition="WRITE_APPEND",
                    schema=transform_schema(schema),
                ),
            )
            .result()
            .output_rows
        )

    return _load
