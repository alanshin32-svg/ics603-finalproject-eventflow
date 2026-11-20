from collections.abc import Iterator

import pytest
from pydantic_ai.models import override_allow_model_requests


@pytest.fixture(autouse=True)
def disable_real_model_requests() -> Iterator[None]:
    with override_allow_model_requests(False):
        yield
