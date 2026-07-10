import pytest
from app import app, todos


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Tests unitaires ───────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_get_todos(client):
    r = client.get("/todos")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_create_todo(client):
    r = client.post("/todos", json={"title": "Test todo"})
    assert r.status_code == 201
    assert r.get_json()["title"] == "Test todo"
    assert r.get_json()["done"] is False


def test_create_todo_missing_title(client):
    r = client.post("/todos", json={})
    assert r.status_code == 400


def test_create_todo_empty_title(client):
    r = client.post("/todos", json={"title": ""})
    assert r.status_code == 400


def test_get_todo_not_found(client):
    r = client.get("/todos/9999")
    assert r.status_code == 404


def test_update_todo(client):
    r = client.put("/todos/1", json={"done": True})
    assert r.status_code == 200
    assert r.get_json()["done"] is True


def test_update_todo_not_found(client):
    r = client.put("/todos/9999", json={"done": True})
    assert r.status_code == 404


def test_delete_todo(client):
    r = client.post("/todos", json={"title": "To delete"})
    tid = r.get_json()["id"]
    r = client.delete(f"/todos/{tid}")
    assert r.status_code == 200
    assert r.get_json()["deleted"] == tid


def test_delete_todo_not_found(client):
    r = client.delete("/todos/9999")
    assert r.status_code == 404


def test_stats(client):
    r = client.get("/stats")
    assert r.status_code == 200
    data = r.get_json()
    assert "total" in data
    assert "done" in data
    assert "pending" in data
    assert data["total"] == data["done"] + data["pending"]


@pytest.mark.parametrize("title,expected", [
    ("Valid todo", 201),
    ("", 400),
    ("A" * 200, 201),
])
def test_create_todo_parametrized(client, title, expected):
    r = client.post("/todos", json={"title": title})
    assert r.status_code == expected


# ── Tests d'intégration ───────────────────────────────────────────────────────

class TestTodoCRUDWorkflow:
    """Workflow complet : créer → lire → modifier → supprimer."""

    def test_complete_lifecycle(self, client):
        # Créer
        r = client.post("/todos", json={"title": "Integration test"})
        assert r.status_code == 201
        tid = r.get_json()["id"]

        # Lire dans la liste
        r = client.get("/todos")
        ids = [t["id"] for t in r.get_json()]
        assert tid in ids

        # Récupérer par ID
        r = client.get(f"/todos/{tid}")
        assert r.status_code == 200
        assert r.get_json()["done"] is False

        # Marquer terminé
        r = client.put(f"/todos/{tid}", json={"done": True})
        assert r.get_json()["done"] is True

        # Vérifier stats
        r = client.get("/stats")
        assert r.get_json()["done"] >= 1

        # Supprimer
        r = client.delete(f"/todos/{tid}")
        assert r.status_code == 200

        # Vérifier 404
        r = client.get(f"/todos/{tid}")
        assert r.status_code == 404

    def test_stats_consistency(self, client):
        """Les stats doivent toujours être cohérentes."""
        ids = []
        for i in range(3):
            r = client.post("/todos", json={"title": f"Stats test {i}"})
            ids.append(r.get_json()["id"])

        client.put(f"/todos/{ids[0]}", json={"done": True})
        client.put(f"/todos/{ids[1]}", json={"done": True})

        r = client.get("/stats")
        stats = r.get_json()
        assert stats["total"] == stats["done"] + stats["pending"]
