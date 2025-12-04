"""
Test Chat History Fix
Verify that AI remembers conversation context
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_chat_history():
    print("🧪 Testing Chat History Fix...\n")
    
    # 1. Register test user
    print("1️⃣ Registering test user...")
    register_data = {
        "username": "test_history",
        "email": "test_history@example.com",
        "password": "test123",
        "full_name": "Test User",
        "role": "student"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if resp.status_code == 200:
            print("   ✅ User registered")
        else:
            print(f"   ℹ️ User exists (status {resp.status_code})")
    except Exception as e:
        print(f"   ⚠️ Register error: {e}")
    
    # 2. Login
    print("\n2️⃣ Logging in...")
    login_data = {
        "username": "test_history",
        "password": "test123"
    }
    
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if resp.status_code != 200:
        print(f"   ❌ Login failed: {resp.text}")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   ✅ Logged in")
    
    # 3. Create chat session
    print("\n3️⃣ Creating chat session...")
    session_data = {"title": "Test History"}
    resp = requests.post(f"{BASE_URL}/chat/sessions", json=session_data, headers=headers)
    
    if resp.status_code != 200:
        print(f"   ❌ Session creation failed: {resp.text}")
        return
    
    session_id = resp.json()["id"]
    print(f"   ✅ Session created (ID: {session_id})")
    
    # 4. Test conversation
    print("\n4️⃣ Testing conversation context...\n")
    
    messages = [
        "Xin chào",
        "Tên tôi là An",
        "Tên tôi là gì?"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"   👤 User: {msg}")
        
        msg_data = {"content": msg}
        resp = requests.post(
            f"{BASE_URL}/chat/sessions/{session_id}/messages",
            json=msg_data,
            headers=headers
        )
        
        if resp.status_code != 200:
            print(f"   ❌ Send message failed: {resp.text}")
            continue
        
        ai_response = resp.json()["content"]
        print(f"   🤖 AI: {ai_response[:100]}...")
        
        # Check if AI remembers name in message 3
        if i == 3:
            if "an" in ai_response.lower():
                print("\n✅ SUCCESS! AI nhớ tên người dùng!")
                print("   Chat history đã được FIX!")
            else:
                print("\n⚠️ WARNING: AI không nhớ tên")
                print("   Response:", ai_response)
        
        print()
    
    # 5. Cleanup
    print("\n5️⃣ Cleaning up...")
    requests.delete(f"{BASE_URL}/chat/sessions/{session_id}", headers=headers)
    print("   ✅ Test session deleted")
    
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    test_chat_history()

