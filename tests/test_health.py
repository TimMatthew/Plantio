import pytest


@pytest.mark.asyncio
async def test_health_model(client):
    r = await client.get("/api/v1/health/model")
    assert r.status_code == 200
    js = r.json()
    assert "backend" in js


@pytest.mark.asyncio
async def test_health_db(client):
    r = await client.get("/api/v1/health/db")
    assert r.status_code in (200, 503)


@pytest.mark.asyncio
async def test_health_app(client):
    r = await client.get("/api/v1/health/app")
    assert r.status_code == 200
    js = r.json()
    assert "app" in js and "version" in js and "env" in js
