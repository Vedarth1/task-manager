from datetime import datetime

def test_create_read_update_delete_task(client):
    login = client.post("/auth/login", data={"username": "test@example.com", "password": "password123"})
    token_data = login.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    task_data = {
        "title": "Test Task",
        "description": "pending",
        "assigned_to": "a6217e33-0eb5-4b69-88ee-8cdfd9f893b0",
        "due_date": datetime(2025, 4, 5, 4, 58, 17).isoformat(),
        "priority": "low"
    }


    res = client.post("/tasks/", json=task_data, headers=headers)
    print(res.status_code)
    print(res.json()) 
    assert res.status_code == 200
    task = res.json()
    task_id = task["task_id"]

    res = client.get(f"/tasks/{task_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Test Task"

    res = client.put(f"/tasks/{task_id}", json={"title": "Updated"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Updated"

    res = client.delete(f"/tasks/{task_id}", headers=headers)
    assert res.status_code == 200