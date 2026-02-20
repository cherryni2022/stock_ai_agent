---
name: sse-streaming
description: SSE (Server-Sent Events) streaming response patterns for the Stock AI Agent project. Use when implementing FastAPI StreamingResponse with asyncio.Queue for real-time progress updates, defining SSE event types (status/chunk/result/error/DONE), building Streamlit EventSource consumers, adding heartbeat mechanisms, or handling SSE error recovery. Triggers on any SSE, streaming response, real-time progress, or event stream implementation task.
---

# SSE Streaming Patterns

## Architecture Overview

```
Agent Node → status_callback() → asyncio.Queue → StreamingResponse → Client (SSE)
```

The LangGraph agent pushes status updates via a callback injected into `AgentState`.
The FastAPI endpoint reads from the queue and streams as SSE events.

## Event Types

| Event Type | When | Payload |
|-----------|------|---------|
| `status` | Agent processing phase changes | `{"type":"status", "status":"analyzing\|planning\|retrieving\|synthesizing"}` |
| `chunk` | Streaming LLM text generation | `{"type":"chunk", "content":"partial text"}` |
| `result` | Final agent response ready | `{"type":"result", "content":"...", "sources":[...], "disclaimer":"..."}` |
| `error` | Unrecoverable error | `{"type":"error", "message":"...", "code":"..."}` |
| `[DONE]` | Stream termination signal | Raw string, not JSON |

## FastAPI SSE Endpoint

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter(prefix="/api")

@router.post("/chat")
async def chat(request: ChatRequest):
    async def event_stream():
        queue: asyncio.Queue = asyncio.Queue()

        async def status_callback(event: dict):
            """Injected into AgentState for nodes to push updates."""
            await queue.put(event)

        # Initialize agent state with callback
        initial_state: AgentState = {
            "session_id": request.session_id or str(uuid.uuid4()),
            "messages": [HumanMessage(content=request.message)],
            "status_callback": status_callback,
            # ... other state fields
        }

        # Launch agent in background
        agent_task = asyncio.create_task(agent.ainvoke(initial_state))

        # Stream events from queue
        while not agent_task.done():
            try:
                event = await asyncio.wait_for(queue.get(), timeout=0.5)
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            except asyncio.TimeoutError:
                continue

        # Final result
        final_state = agent_task.result()
        yield f"data: {json.dumps({
            'type': 'result',
            'content': final_state['analysis_result'],
            'sources': final_state['data_sources'],
            'disclaimer': final_state['risk_disclaimer'],
        }, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx compatibility
        },
    )
```

## Pushing Status from Agent Nodes

Every agent node can push status updates:

```python
async def intent_node(state: AgentState) -> dict:
    # ... do work ...
    if state.get("status_callback"):
        await state["status_callback"]({"type": "status", "status": "analyzing"})
    return {"intent": intent}
```

## Streamlit SSE Consumer

```python
import sseclient
import requests

def stream_chat(message: str, base_url: str):
    response = requests.post(
        f"{base_url}/api/chat",
        json={"message": message},
        stream=True,
    )
    client = sseclient.SSEClient(response)
    for event in client.events():
        if event.data == "[DONE]":
            break
        data = json.loads(event.data)
        if data["type"] == "status":
            st.status(data["status"])
        elif data["type"] == "chunk":
            yield data["content"]
        elif data["type"] == "result":
            yield data["content"]
```

## JavaScript SSE Consumer

```javascript
const eventSource = new EventSource('/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: userInput}),
});

eventSource.onmessage = (event) => {
  if (event.data === '[DONE]') {
    eventSource.close();
    return;
  }
  const data = JSON.parse(event.data);
  switch (data.type) {
    case 'status': updateStatusUI(data.status); break;
    case 'chunk':  appendText(data.content); break;
    case 'result': showFinalResult(data); break;
    case 'error':  showError(data.message); break;
  }
};
```

## Error Handling

Wrap the entire `event_stream()` generator in try/except:

```python
async def event_stream():
    try:
        # ... normal flow ...
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
```

## Heartbeat (for long-running queries)

```python
# Send periodic heartbeat to prevent proxy/client timeouts
HEARTBEAT_INTERVAL = 15  # seconds

async def event_stream():
    last_event_time = time.time()
    while not agent_task.done():
        try:
            event = await asyncio.wait_for(queue.get(), timeout=0.5)
            yield f"data: {json.dumps(event)}\n\n"
            last_event_time = time.time()
        except asyncio.TimeoutError:
            if time.time() - last_event_time > HEARTBEAT_INTERVAL:
                yield ": heartbeat\n\n"  # SSE comment syntax
                last_event_time = time.time()
```
