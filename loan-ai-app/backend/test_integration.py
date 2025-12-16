"""
Integration test script for AI Loan Sales Platform
Tests the complete flow from greeting to decision
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("🧪 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed")
    return True

def test_full_flow():
    """Test complete loan application flow"""
    print("\n🧪 Testing Full Loan Application Flow")
    
    # 1. Health check
    test_health_check()
    
    # 2. Start conversation
    conv_id = None
    print("\n📝 Step 1: Starting conversation...")
    
    # 3. Send greeting
    print("📝 Step 2: Sending greeting...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Hi, I need a loan"
    })
    assert response.status_code == 200
    data = response.json()
    conv_id = data.get("conversation_id")
    assert conv_id is not None
    print(f"✅ Conversation started: {conv_id}")
    print(f"   Response: {data.get('message', '')[:100]}...")
    
    # 4. Provide loan details
    print("\n📝 Step 3: Providing loan details...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "conversation_id": conv_id,
        "message": "I need ₹100000 for business expansion"
    })
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Loan details provided")
    print(f"   Stage: {data.get('stage')}")
    
    # 5. Provide name
    print("\n📝 Step 4: Providing name...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "conversation_id": conv_id,
        "message": "My name is John Doe"
    })
    assert response.status_code == 200
    print("✅ Name provided")
    
    # 6. Provide salary
    print("\n📝 Step 5: Providing salary...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "conversation_id": conv_id,
        "message": "My salary is ₹50000 per month"
    })
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Salary provided")
    print(f"   Stage: {data.get('stage')}")
    
    # 7. Provide employment type
    print("\n📝 Step 6: Providing employment type...")
    response = requests.post(f"{BASE_URL}/api/chat", json={
        "conversation_id": conv_id,
        "message": "I am salaried"
    })
    assert response.status_code == 200
    print("✅ Employment type provided")
    
    # 8. Check conversation state
    print("\n📝 Step 7: Checking conversation state...")
    response = requests.get(f"{BASE_URL}/api/conversation/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Conversation state retrieved")
    print(f"   Stage: {data.get('stage')}")
    print(f"   Messages: {len(data.get('messages', []))}")
    print(f"   Decision: {data.get('decision')}")
    
    # 9. Test stats endpoint
    print("\n📝 Step 8: Testing stats endpoint...")
    response = requests.get(f"{BASE_URL}/api/stats")
    assert response.status_code == 200
    stats = response.json()
    print(f"✅ Stats retrieved")
    print(f"   Total conversations: {stats.get('total_conversations')}")
    print(f"   Approved: {stats.get('approved_loans')}")
    print(f"   Rejected: {stats.get('rejected_loans')}")
    print(f"   Pending: {stats.get('pending')}")
    
    print("\n🎉 Integration test completed successfully!")
    return True

def test_error_handling():
    """Test error handling"""
    print("\n🧪 Testing Error Handling...")
    
    # Test invalid conversation ID
    response = requests.get(f"{BASE_URL}/api/conversation/invalid_id")
    assert response.status_code == 404
    print("✅ Invalid conversation ID handled correctly")
    
    # Test missing message
    response = requests.post(f"{BASE_URL}/api/chat", json={})
    assert response.status_code == 422  # Validation error
    print("✅ Missing message handled correctly")
    
    print("✅ Error handling tests passed")

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("AI Loan Sales Platform - Integration Tests")
        print("=" * 60)
        
        test_full_flow()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server. Make sure backend is running on http://localhost:8000")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)


