"""Compatibility tests for mocking popular `requests` workflows with MockSafe.

These tests intentionally avoid real network calls and instead focus on patterns
developers commonly use in application code:
- module-level helpers (e.g. ``requests.get``)
- session-based calls (e.g. ``requests.Session.request``)
- error paths via ``requests.exceptions``
"""

from __future__ import annotations

from typing import Any

import pytest

from mocksafe import mock, mock_module, that, when

requests = pytest.importorskip("requests")


def test_requests_module_get_with_kwargs_and_json_response() -> None:
    mock_requests = mock_module(requests)
    mock_response = mock(requests.Response)
    payload: dict[str, Any] = {"status": "ok", "count": 2}

    when(mock_response.json).any_call().then_return(payload)
    when(mock_requests.get).called_with(
        mock_requests.get(
            "https://api.example.com/widgets",
            params={"kind": "popular"},
            headers={"x-request-id": "abc123"},
            timeout=1.5,
        )
    ).then_return(mock_response)

    response = mock_requests.get(
        "https://api.example.com/widgets",
        params={"kind": "popular"},
        headers={"x-request-id": "abc123"},
        timeout=1.5,
    )

    assert response.json() == payload
    assert that(mock_requests.get).was_called
    assert that(mock_requests.get).last_call == (
        ("https://api.example.com/widgets",),
        {
            "params": {"kind": "popular"},
            "headers": {"x-request-id": "abc123"},
            "timeout": 1.5,
        },
    )


def test_requests_module_get_timeout_error_path() -> None:
    mock_requests = mock_module(requests)

    when(mock_requests.get).any_call().then_raise(
        requests.exceptions.Timeout("request timed out")
    )

    with pytest.raises(requests.exceptions.Timeout):
        mock_requests.get("https://api.example.com/slow", timeout=0.1)

    assert that(mock_requests.get).num_calls == 1


def test_requests_session_request_happy_path() -> None:
    mock_session = mock(requests.Session)
    mock_response = mock(requests.Response)

    when(mock_response.json).any_call().then_return({"id": "w-42"})
    when(mock_session.request).called_with(
        mock_session.request("GET", "https://api.example.com/widgets/w-42", timeout=2.0)
    ).then_return(mock_response)

    response = mock_session.request(
        "GET", "https://api.example.com/widgets/w-42", timeout=2.0
    )

    assert response.json()["id"] == "w-42"
    assert that(mock_session.request).last_call == (
        ("GET", "https://api.example.com/widgets/w-42"),
        {"timeout": 2.0},
    )


def test_requests_response_raise_for_status_error_path() -> None:
    mock_response = mock(requests.Response)

    when(mock_response.raise_for_status).any_call().then_raise(
        requests.exceptions.HTTPError("500 Server Error")
    )

    with pytest.raises(requests.exceptions.HTTPError):
        mock_response.raise_for_status()

    assert that(mock_response.raise_for_status).was_called


def test_requests_module_get_multiple_calls_and_call_history() -> None:
    mock_requests = mock_module(requests)
    mock_response = mock(requests.Response)

    when(mock_requests.get).any_call().then_return(mock_response)

    mock_requests.get("https://api.example.com/one")
    mock_requests.get("https://api.example.com/two")
    mock_requests.get("https://api.example.com/three")

    assert that(mock_requests.get).num_calls == 3
    assert that(mock_requests.get).nth_call(1) == ("https://api.example.com/two",)
    assert that(mock_requests.get).last_call == ("https://api.example.com/three",)
