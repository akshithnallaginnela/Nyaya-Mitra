# WebSocket Streaming Endpoint

## Overview

The WebSocket streaming endpoint (`/api/chat/stream`) enables real-time streaming of AI responses, providing a better user experience by showing responses as they are generated rather than waiting for the complete response.

## Endpoint

```
ws://localhost:8000/api/chat/stream
```

## Protocol

### 1. Connection

Connect to the WebSocket endpoint using any WebSocket client.

### 2. Authentication

**Client sends:**
```json
{
  "type": "auth",
  "token": "YOUR_JWT_TOKEN"
}
```

**Server responds:**
```json
{
  "type": "auth_success",
  "data": {
    "user_id": "user-uuid"
  }
}
```

**On error:**
```json
{
  "type": "error",
  "data": {
    "message": "Authentication failed: ..."
  }
}
```

### 3. Query

**Client sends:**
```json
{
  "type": "query",
  "query": "What is IPC Section 499?",
  "language": "en",
  "conversation_id": 123  // optional
}
```

### 4. Streaming Response

**Server sends multiple messages:**

**Metadata (first):**
```json
{
  "type": "metadata",
  "data": {
    "confidence": 0.85,
    "language": "en",
    "needs_clarification": false
  }
}
```

**Tokens (multiple, streamed):**
```json
{
  "type": "token",
  "data": {
    "content": "IPC Section 499 "
  }
}
```

**Citations:**
```json
{
  "type": "citations",
  "data": {
    "citations": [
      {
        "type": "IPC",
        "section": "499",
        "text": "IPC Section 499"
      }
    ]
  }
}
```

**Complete (last):**
```json
{
  "type": "complete",
  "data": {
    "conversation_id": 123,
    "message_id": 456,
    "confidence": 0.85,
    "needs_clarification": false
  }
}
```

**On error:**
```json
{
  "type": "error",
  "data": {
    "message": "Error processing query: ..."
  }
}
```

## Connection Handling

### Reconnection

The WebSocket endpoint supports automatic reconnection. Clients should implement exponential backoff for reconnection attempts:

```javascript
let reconnectDelay = 1000; // Start with 1 second
const maxReconnectDelay = 30000; // Max 30 seconds

function connect() {
  const ws = new WebSocket('ws://localhost:8000/api/chat/stream');
  
  ws.onclose = () => {
    console.log('Disconnected, reconnecting in', reconnectDelay, 'ms');
    setTimeout(() => {
      reconnectDelay = Math.min(reconnectDelay * 2, maxReconnectDelay);
      connect();
    }, reconnectDelay);
  };
  
  ws.onopen = () => {
    reconnectDelay = 1000; // Reset delay on successful connection
  };
}
```

### Error Handling

- **Connection errors**: The server will send an error message and close the connection
- **Authentication errors**: Connection closed with code 1008 (Policy Violation)
- **Query errors**: Error message sent, connection remains open for retry

## Example Client (JavaScript)

```javascript
const token = 'YOUR_JWT_TOKEN';
const ws = new WebSocket('ws://localhost:8000/api/chat/stream');

ws.onopen = () => {
  console.log('Connected');
  
  // Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: token
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'auth_success':
      console.log('Authenticated');
      
      // Send query
      ws.send(JSON.stringify({
        type: 'query',
        query: 'What is IPC Section 499?',
        language: 'en'
      }));
      break;
      
    case 'metadata':
      console.log('Confidence:', message.data.confidence);
      break;
      
    case 'token':
      // Append token to response display
      document.getElementById('response').textContent += message.data.content;
      break;
      
    case 'citations':
      console.log('Citations:', message.data.citations);
      break;
      
    case 'complete':
      console.log('Response complete');
      break;
      
    case 'error':
      console.error('Error:', message.data.message);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

## Example Client (Python)

```python
import asyncio
import websockets
import json

async def chat_stream():
    token = 'YOUR_JWT_TOKEN'
    uri = 'ws://localhost:8000/api/chat/stream'
    
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            'type': 'auth',
            'token': token
        }))
        
        auth_response = json.loads(await websocket.recv())
        if auth_response['type'] != 'auth_success':
            print('Authentication failed')
            return
        
        # Send query
        await websocket.send(json.dumps({
            'type': 'query',
            'query': 'What is IPC Section 499?',
            'language': 'en'
        }))
        
        # Receive streaming response
        while True:
            response = json.loads(await websocket.recv())
            
            if response['type'] == 'token':
                print(response['data']['content'], end='', flush=True)
            elif response['type'] == 'complete':
                print('\nComplete!')
                break
            elif response['type'] == 'error':
                print(f"\nError: {response['data']['message']}")
                break

asyncio.run(chat_stream())
```

## Testing

### Manual Testing

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. Run the manual test script:
   ```bash
   python test_websocket_manual.py
   ```

3. Update the token in the script with a valid JWT token from the authentication endpoint.

### Using WebSocket Client Tools

You can also test using WebSocket client tools like:
- **wscat**: `wscat -c ws://localhost:8000/api/chat/stream`
- **Postman**: Supports WebSocket connections
- **Browser DevTools**: Use the WebSocket API in the browser console

## Performance Considerations

- **Response Time**: Tokens are streamed as they are generated by the AI model, typically within milliseconds of each other
- **Connection Limit**: The server can handle multiple concurrent WebSocket connections
- **Timeout**: Connections will timeout after 30 seconds of inactivity
- **Message Size**: Each token message is typically small (a few bytes to a few hundred bytes)

## Security

- **Authentication Required**: All WebSocket connections must authenticate with a valid JWT token
- **Token Validation**: Tokens are validated on connection and must not be expired
- **User Isolation**: Each connection is isolated to the authenticated user's data
- **Connection Closure**: Connections are automatically closed on authentication failure

## Requirements Validation

This implementation satisfies **Requirement 1.1**:
- ✓ AI responses are generated and streamed in real-time
- ✓ Response time is optimized by streaming tokens as they are generated
- ✓ Users see responses appearing progressively rather than waiting for completion
- ✓ Connection errors and reconnection are handled gracefully

## Future Enhancements

Potential improvements for future versions:
- **Typing Indicators**: Show when the AI is "thinking" before tokens start streaming
- **Progress Updates**: Show progress for long-running queries
- **Cancellation**: Allow users to cancel in-progress queries
- **Rate Limiting**: Implement per-user rate limiting for WebSocket connections
- **Compression**: Enable WebSocket compression for reduced bandwidth usage
