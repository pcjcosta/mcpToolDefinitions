# Architecture overview - Model Context Protocol

This overview of the Model Context Protocol (MCP) discusses its scope and core concepts, and provides an example demonstrating each core concept.

## Scope

The Model Context Protocol includes the following projects:

* MCP Specification: A specification of MCP that outlines the implementation requirements for clients and servers.
* MCP SDKs: SDKs for different programming languages that implement MCP.
* MCP Development Tools: Tools for developing MCP servers and clients, including the MCP Inspector
* MCP Reference Server Implementations: Reference implementations of MCP servers.

MCP focuses solely on the protocol for context exchange—it does not dictate how AI applications use LLMs or manage the provided context.

## Concepts of MCP

### Participants

MCP follows a client-server architecture where an MCP host — an AI application like Claude Code or Claude Desktop — establishes connections to one or more MCP servers. The MCP host accomplishes this by creating one MCP client for each MCP server. Each MCP client maintains a dedicated one-to-one connection with its corresponding MCP server. The key participants in the MCP architecture are:

* MCP Host: The AI application that coordinates and manages one or multiple MCP clients
* MCP Client: A component that maintains a connection to an MCP server and obtains context from an MCP server for the MCP host to use
* MCP Server: A program that provides context to MCP clients

### Layers

MCP consists of two layers:

* Data layer: Defines the JSON-RPC based protocol for client-server communication, including lifecycle management, and core primitives, such as tools, resources, prompts and notifications.
* Transport layer: Defines the communication mechanisms and channels that enable data exchange between clients and servers, including transport-specific connection establishment, message framing, and authorization.

#### Data layer

The data layer implements a JSON-RPC 2.0 based exchange protocol that defines the message structure and semantics. This layer includes:

* Lifecycle management: Handles connection initialization, capability negotiation, and connection termination between clients and servers
* Server features: Enables servers to provide core functionality including tools for AI actions, resources for context data, and prompts for interaction templates from an MCP server to the client
* Client features: Enables servers to ask the client to sample from the host LLM, elicit input from the user, and log messages to the client
* Utility features: Supports additional capabilities like notifications for real-time updates and progress tracking for long-running operations

#### Transport layer

The transport layer manages communication channels and authentication between clients and servers. It handles connection establishment, message framing, and secure communication between MCP participants. MCP supports two transport mechanisms:

* Stdio transport: Uses standard input/output streams for direct process communication between local processes on the same machine, providing optimal performance with no network overhead.
* Streamable HTTP transport: Uses HTTP POST for client-to-server messages with optional Server-Sent Events for streaming capabilities. This transport enables remote server communication and supports standard HTTP authentication methods including bearer tokens, API keys, and custom headers. MCP recommends using OAuth to obtain authentication tokens.

### Data Layer Protocol

A core part of MCP is defining the schema and semantics between MCP clients and MCP servers. MCP uses JSON-RPC 2.0 as its underlying RPC protocol. Client and servers send requests to each other and respond accordingly. Notifications can be used when no response is required.

#### Lifecycle management

MCP is a protocol that requires lifecycle management. The purpose of lifecycle management is to negotiate the capabilities that both client and server support.

#### Primitives

MCP primitives are the most important concept within MCP. They define what clients and servers can offer each other. These primitives specify the types of contextual information that can be shared with AI applications and the range of actions that can be performed. MCP defines three core primitives that servers can expose:

* Tools: Executable functions that AI applications can invoke to perform actions (e.g., file operations, API calls, database queries)
* Resources: Data sources that provide contextual information to AI applications (e.g., file contents, database records, API responses)
* Prompts: Reusable templates that help structure interactions with language models (e.g., system prompts, few-shot examples)

Each primitive type has associated methods for discovery (*/list), retrieval (*/get), and in some cases, execution (tools/call).

MCP also defines primitives that clients can expose:

* Sampling: Allows servers to request language model completions from the client's AI application
* Elicitation: Allows servers to request additional information from users
* Logging: Enables servers to send log messages to clients for debugging and monitoring purposes

#### Notifications

The protocol supports real-time notifications to enable dynamic updates between servers and clients. For example, when a server's available tools change—such as when new functionality becomes available or existing tools are modified—the server can send tool update notifications to inform connected clients about these changes.

## Example

### Data Layer

#### Initialization (Lifecycle Management)

MCP begins with lifecycle management through a capability negotiation handshake:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "elicitation": {}
    },
    "clientInfo": {
      "name": "example-client",
      "version": "1.0.0"
    }
  }
}
```

The initialization process serves several critical purposes:
1. Protocol Version Negotiation
2. Capability Discovery
3. Identity Exchange

After successful initialization, the client sends a notification to indicate it's ready:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

#### Tool Discovery (Primitives)

The client can discover available tools by sending a tools/list request:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

The response contains a tools array that provides comprehensive metadata about each available tool.

#### Tool Execution (Primitives)

The client can execute a tool using the tools/call method:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "weather_current",
    "arguments": {
      "location": "San Francisco",
      "units": "imperial"
    }
  }
}
```

The response provides structured output that the AI application can use as context.

#### Real-time Updates (Notifications)

MCP supports real-time notifications that enable servers to inform clients about changes:

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}
```

Upon receiving this notification, the client typically reacts by requesting the updated tool list:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/list"
}
```