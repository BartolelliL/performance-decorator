from performance import performance


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
