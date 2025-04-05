from fastapi import BackgroundTasks

def dummy_task(title: str):
    dummy_task.executed = True

def test_background_task_trigger():
    dummy_task.executed = False
    dummy_task("Title")

    assert dummy_task.executed is True
