import pytest


@pytest.mark.asyncio
async def test_diagnose_success(
    client,
    sample_jpeg_bytes,
    mock_storage_save,
    mock_plant_find_one,
    mock_diagnosis_insert,
    mock_inference_success,
):
    files = {"image": ("test.jpg", sample_jpeg_bytes, "image/jpeg")}
    data = {"topK": "3", "threshold": "0.2"}

    r = await client.post("/api/v1/diagnose", files=files, data=data)
    assert r.status_code == 200, r.text
    js = r.json()
    assert js["diagnosisId"] == "test-diagnosis-id"
    assert js["decidedDiseaseId"] == "Grape Esca (Black Measles)"
    assert isinstance(js["inferenceMs"], int)
    assert js["candidates"][0]["plant_name"] in ("Виноград", "Соняшник")


@pytest.mark.asyncio
async def test_diagnose_low_confidence(
    client,
    sample_jpeg_bytes,
    mock_storage_save,
    mock_plant_find_one,
    mock_diagnosis_insert,
    mock_inference_low,
):
    files = {"image": ("test.jpg", sample_jpeg_bytes, "image/jpeg")}
    data = {"topK": "3", "threshold": "0.2"}

    r = await client.post("/api/v1/diagnose", files=files, data=data)
    assert r.status_code == 422
    js = r.json()
    assert js["detail"]["message"] == "low_confidence"
    assert isinstance(js["detail"]["candidates"], list)
