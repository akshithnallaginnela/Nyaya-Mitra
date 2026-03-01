"""
Manual test script for WebSocket streaming endpoint.

This script demonstrates how to connect to the WebSocket endpoint
and stream AI responses in real-time.

Usage:
1. Start the FastAPI server: uvicorn main:app --reload
2. Run this script: python test_websocket_manual.py
"""
import asyncio
import websockets
import json


async def test_websocket_stream():
    """Test WebSocket streaming with a sample query."""
    
    # Note: Replace with a valid JWT token from your authentication endpoint
    # You can get a token by:
    # 1. Register a user: POST /api/auth/register
    # 2. Login: POST /api/auth/login
    # 3. Use the returned token
    
    token = "YOUR_JWT_TOKEN_HERE"
    
    uri = "ws://localhost:8000/api/chat/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            # Step 1: Authenticate
            auth_message = {
                "type": "auth",
                "token": token
            }
            await websocket.send(json.dumps(auth_message))
            print(f"Sent: {auth_message}")
            
            # Receive auth response
            response = await websocket.recv()
            auth_response = json.loads(response)
            print(f"Received: {auth_response}")
            
            if auth_response["type"] != "auth_success":
                print("Authentication failed!")
                return
            
            print("Authentication successful!")
            
            # Step 2: Send query
            query_message = {
                "type": "query",
                "query": "What is IPC Section 499?",
                "language": "en"
            }
            await websocket.send(json.dumps(query_message))
            print(f"\nSent query: {query_message['query']}")
            
            # Step 3: Receive streaming response
            print("\nStreaming response:")
            print("-" * 50)
            
            full_response = ""
            
            while True:
                try:
                    response = await websocket.recv()
                    chunk = json.loads(response)
                    
                    if chunk["type"] == "metadata":
                        print(f"\nMetadata:")
                        print(f"  Confidence: {chunk['data']['confidence']:.2f}")
                        print(f"  Language: {chunk['data']['language']}")
                        print(f"  Needs clarification: {chunk['data']['needs_clarification']}")
                        print("\nResponse:")
                    
                    elif chunk["type"] == "token":
                        # Print token without newline to show streaming effect
                        token_text = chunk["data"]["content"]
                        print(token_text, end="", flush=True)
                        full_response += token_text
                    
                    elif chunk["type"] == "citations":
                        print("\n\nCitations:")
                        for citation in chunk["data"]["citations"]:
                            print(f"  - {citation.get('text', citation)}")
                    
                    elif chunk["type"] == "complete":
                        print("\n\nComplete!")
                        print(f"Conversation ID: {chunk['data']['conversation_id']}")
                        print(f"Message ID: {chunk['data']['message_id']}")
                        break
                    
                    elif chunk["type"] == "error":
                        print(f"\nError: {chunk['data']['message']}")
                        break
                        
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed")
                    break
            
            print("-" * 50)
            print(f"\nFull response length: {len(full_response)} characters")
            
    except Exception as e:
        print(f"Error: {e}")


async def test_websocket_without_auth():
    """Test WebSocket without authentication (should fail)."""
    uri = "ws://localhost:8000/api/chat/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            # Try to send query without auth
            query_message = {
                "type": "query",
                "query": "Test query"
            }
            await websocket.send(json.dumps(query_message))
            
            # Should receive error
            response = await websocket.recv()
            error_response = json.loads(response)
            print(f"Received: {error_response}")
            
            if error_response["type"] == "error":
                print("✓ Correctly rejected unauthenticated request")
            else:
                print("✗ Should have rejected unauthenticated request")
                
    except Exception as e:
        print(f"Error: {e}")


async def test_websocket_invalid_token():
    """Test WebSocket with invalid token (should fail)."""
    uri = "ws://localhost:8000/api/chat/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")
            
            # Send invalid token
            auth_message = {
                "type": "auth",
                "token": "invalid_token_12345"
            }
            await websocket.send(json.dumps(auth_message))
            
            # Should receive error
            response = await websocket.recv()
            error_response = json.loads(response)
            print(f"Received: {error_response}")
            
            if error_response["type"] == "error":
                print("✓ Correctly rejected invalid token")
            else:
                print("✗ Should have rejected invalid token")
                
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all tests."""
    print("=" * 50)
    print("WebSocket Streaming Tests")
    print("=" * 50)
    
    print("\n1. Testing without authentication:")
    print("-" * 50)
    await test_websocket_without_auth()
    
    print("\n\n2. Testing with invalid token:")
    print("-" * 50)
    await test_websocket_invalid_token()
    
    print("\n\n3. Testing with valid token:")
    print("-" * 50)
    print("Note: Update the token in test_websocket_stream() function")
    print("      to test with a valid JWT token")
    # Uncomment to test with valid token:
    # await test_websocket_stream()
    
    print("\n" + "=" * 50)
    print("Tests complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
