from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health():
    response=client.get("/api/v1/health")
    assert response.status_code==200
    assert response.json()["status"]=="ok"

def test_unsupported_file():
    response=client.post("/api/v1/documents/process",
                         files={"file":("test.txt",b"hello","text/plain")},
                         data={"document_type":"invoice"})
    assert response.status_code==415
