import asyncio

from performance import performance


def test_performance_has_ide_friendly_documentation():
    assert "wrapped.last_duration" in performance.__doc__
    assert "``" not in performance.__doc__
    assert ":func:" not in performance.__doc__


def test_performance_preserves_result_and_records_duration(capsys):
    @performance
    def add(left, right):
        return left + right

    assert add(2, 3) == 5
    assert add.last_duration is not None
    assert add.last_duration >= 0
    assert len(add.execution_times) == 1
    assert "add took " in capsys.readouterr().out


def test_performance_records_duration_when_function_raises():
    @performance
    def fail():
        raise ValueError("failed")

    try:
        fail()
    except ValueError:
        pass

    assert fail.last_duration is not None
    assert len(fail.execution_times) == 1


def test_performance_supports_bounded_history_and_callback(capsys):
    timings = []

    @performance(history_size=2, on_complete=timings.append)
    def identity(value):
        return value

    identity(1)
    identity(2)
    identity(3)

    assert len(identity.execution_times) == 2
    assert identity.execution_times == [identity.execution_times[0], identity.last_duration]
    assert timings[-1].function_name == "identity"
    assert timings[-1].succeeded
    assert capsys.readouterr().out.count("identity took") == 3


def test_performance_supports_async_functions():
    @performance(log=None, history_size=0)
    async def get_value():
        return 42

    assert asyncio.run(get_value()) == 42
    assert get_value.last_duration is not None
    assert get_value.execution_times == []
