import asyncio
import pytest
from mocksafe import mock, when_async, that


class MyService:
    async def fetch(self, _url: str) -> str:
        return "real"  # pragma: no cover

    async def compute(self, x: int) -> int:
        return x * 2  # pragma: no cover

    async def risky(self) -> str:
        return "ok"  # pragma: no cover

    def sync_method(self) -> str:
        return "sync"  # pragma: no cover


def test_when_async_any_call_then_return():
    svc = mock(MyService)
    when_async(svc.fetch).any_call().then_return("mocked")
    result = asyncio.run(svc.fetch("http://example.com"))
    assert result == "mocked"


def test_when_async_multiple_sequential_results():
    svc = mock(MyService)
    when_async(svc.compute).any_call().then_return(10, 20, 30)
    assert asyncio.run(svc.compute(0)) == 10
    assert asyncio.run(svc.compute(0)) == 20
    assert asyncio.run(svc.compute(0)) == 30


def test_when_async_called_with():
    async def run() -> None:
        svc = mock(MyService)
        when_async(svc.compute).called_with(await svc.compute(99)).then_return(42)
        assert await svc.compute(99) == 42

    asyncio.run(run())


def test_when_async_then_raise_on_await():
    svc = mock(MyService)
    when_async(svc.risky).any_call().then_raise(RuntimeError("boom"))
    with pytest.raises(RuntimeError, match="boom"):
        asyncio.run(svc.risky())


def test_when_async_that_was_called():
    svc = mock(MyService)
    when_async(svc.fetch).any_call().then_return("x")
    asyncio.run(svc.fetch("a"))
    asyncio.run(svc.fetch("b"))
    assert that(svc.fetch).was_called
    assert that(svc.fetch).num_calls == 2


def test_when_async_spy_last_call_args():
    svc = mock(MyService)
    when_async(svc.fetch).any_call().then_return("x")
    asyncio.run(svc.fetch("hello"))
    assert that(svc.fetch).last_call == ("hello",)


def test_when_async_default_return_for_primitive_type_when_unstubbed():
    svc = mock(MyService)
    # Return type is str, so default is str() == "" (same behaviour as sync)
    result = asyncio.run(svc.risky())
    assert result == ""


def test_when_async_raises_on_sync_method():
    svc = mock(MyService)
    with pytest.raises(TypeError, match="when_async\\(\\) can only be used with async"):
        when_async(svc.sync_method)  # type: ignore[arg-type]
