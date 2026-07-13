from typing import Any

import httpx
from pydantic import BaseModel




def request(
    client: httpx.Client,
    method: str,
    base_url: str,
    path: str,
    *,
    expected_status: int,
    json: BaseModel | dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    if isinstance(json, BaseModel):
        json_body = json.model_dump(
            mode="json",
            by_alias=True,
            exclude_none=True,
        )
    else:
        json_body = json

    response = client.request(
        method,
        f"{base_url}{path}",
        json=json_body,
        params=params,
    )

    print()
    print(f"{method} {response.url}")
    print(f"Status: {response.status_code}")

    if response.content:
        try:
            body = response.json()
            print(body)
        except ValueError:
            body = response.text
            print(body)
    else:
        body = None
        print("(no response body)")

    if response.status_code != expected_status:
        raise RuntimeError(
            f"Expected {expected_status}, got {response.status_code}: {response.text}"
        )

    return body
