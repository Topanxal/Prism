import httpx
import asyncio
import json
import os
import sys

# Add src to path
sys.path.append(os.getcwd())

BASE_URL = "http://127.0.0.1:8000/v1/t2v"

async def test_backend():
    print("🚀 Starting Backend Integration Test (Mock Mode)...")
    
    # 1. Start Server in background (assumed running or we run locally)
    # Ideally, run `uvicorn src.api.main:app --reload` in another terminal
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0, follow_redirects=True, trust_env=False) as client:
        # Check Health
        try:
            resp = await client.get("http://127.0.0.1:8000/health")
            print(f"✅ Health Check: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Health Check Failed: {e}")
            return

        # 2. Test Generation
        print("\nTesting /generate...")
        gen_payload = {
            "user_prompt": "Show me a healthy breakfast with avocado toast",
            "quality_mode": "balanced",
            "resolution": "1280x720"
        }
        resp = await client.post("/generate", json=gen_payload)
        if resp.status_code == 202:
            data = resp.json()
            job_id = data["job_id"]
            print(f"✅ Generation Started: Job ID {job_id}")
        else:
            print(f"❌ Generation Failed: {resp.status_code} - {resp.text}")
            return

        # 3. Poll Status
        print(f"\nPolling status for Job {job_id}...")
        for _ in range(5):
            resp = await client.get(f"/jobs/{job_id}")
            job_data = resp.json()
            state = job_data["status"]
            print(f"Status: {state}")
            if state == "SUCCEEDED":
                print(f"✅ Job Succeeded! Assets: {len(job_data['assets'])}")
                break
            await asyncio.sleep(1)
            
        if state != "SUCCEEDED":
             print("⚠️ Job did not complete in time (Mock mode should be fast)")

        # 4. Test Revision
        print("\nTesting /revise...")
        rev_payload = {
            "feedback": "Make the lighting warmer and add soft music"
        }
        resp = await client.post(f"/jobs/{job_id}/revise", json=rev_payload)
        if resp.status_code == 202:
            rev_data = resp.json()
            rev_job_id = rev_data["job_id"]
            print(f"✅ Revision Started: Job ID {rev_job_id} (Parent: {job_id})")
            print(f"   Targeted Fields: {rev_data['targeted_fields']}")
        else:
            print(f"❌ Revision Failed: {resp.status_code} - {resp.text}")

        # 5. Test Finalization
        print("\nTesting /finalize...")
        fin_payload = {
            "selected_seeds": {1: 12345, 2: 67890},
            "resolution": "1920x1080"
        }
        resp = await client.post(f"/jobs/{job_id}/finalize", json=fin_payload)
        if resp.status_code == 202:
             print(f"✅ Finalization Started")
        else:
             print(f"❌ Finalization Failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    # Check if MOCK_MODE is set
    from src.config.settings import settings
    print(f"Environment: MOCK_MODE={settings.mock_mode}")
    if not settings.mock_mode:
        print("⚠️ WARNING: MOCK_MODE is False. Tests will fail without real API keys.")
    
    # Run tests
    try:
        asyncio.run(test_backend())
    except KeyboardInterrupt:
        print("\nTest interrupted")
    except ConnectionRefusedError:
        print("\n❌ Connection Refused. Is the backend server running?")
        print("Run: uvicorn src.api.main:app --reload")
