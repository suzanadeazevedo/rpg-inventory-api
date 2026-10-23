from fastapi.testclient import TestClient
from app.main import app, get_connection
import app.main as main_module
import sqlite3
import pytest

client = TestClient(app)

def get_test_connection():
    connection = sqlite3.connect("test_inventory.db")
    return connection

@pytest.fixture(autouse=True)
def test_database(monkeypatch):
    connection = get_test_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM items")
    connection.commit()
    connection.close()
    monkeypatch.setattr(main_module, "get_connection", get_test_connection)

def create_test_database():
    connection = get_connection("test_inventory.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT NOT NULL, quantity INTEGER NOT NULL CHECK (quantity >= 0))")
    connection.close()

create_test_database()


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RPG Inventory API funcionando!"}


def test_list_inventory_empty():
    response = client.get("/inventory")
    assert response.json() == []
    assert response.status_code == 200

def test_create_item():
    response = client.post("/item", json = {"name": "pocao", "quantity": 3})
    assert response.status_code == 200
    assert response.json() == {"name": "pocao", "quantity": 3}
    
