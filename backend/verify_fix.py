import requests
import sys
import time

def wait_for_api():
    print("Waiting for API to be ready...")
    for _ in range(10):
        try:
            response = requests.get("http://127.0.0.1:8000/health")
            if response.status_code == 200:
                print("✅ API is ready")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print("❌ API failed to start")
    return False

def test_crud():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Create
    print("\nTesting Create...")
    contact = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890"
    }
    res = requests.post(f"{base_url}/contacts", json=contact)
    if res.status_code != 201:
        print(f"❌ Create failed: {res.text}")
        return
    data = res.json()
    contact_id = data["id"]
    print(f"✅ Created contact ID: {contact_id}")
    
    # 2. Read
    print("\nTesting Read...")
    res = requests.get(f"{base_url}/contacts/{contact_id}")
    if res.status_code == 200 and res.json()["name"] == "Test User":
        print("✅ Read successful")
    else:
        print(f"❌ Read failed: {res.text}")
        
    # 3. Update
    print("\nTesting Update...")
    update_data = {"name": "Updated User"}
    res = requests.put(f"{base_url}/contacts/{contact_id}", json=update_data)
    if res.status_code == 200 and res.json()["name"] == "Updated User":
        print("✅ Update successful")
    else:
        print(f"❌ Update failed: {res.text}")
        
    # 4. Delete
    print("\nTesting Delete...")
    res = requests.delete(f"{base_url}/contacts/{contact_id}")
    if res.status_code == 204:
        print("✅ Delete successful")
    else:
        print(f"❌ Delete failed: {res.text}")

if __name__ == "__main__":
    if wait_for_api():
        test_crud()
