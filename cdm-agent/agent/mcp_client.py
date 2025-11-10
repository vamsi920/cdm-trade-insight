"""
MCP Client Manager for connecting to MCP servers and managing tool discovery
Implements MCP protocol via direct JSON-RPC over stdio for reliability
"""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio.subprocess as subprocess

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MCPClientManager:
    """
    Manages connections to multiple MCP servers and provides unified tool calling interface
    Uses direct JSON-RPC over stdio instead of MCP SDK for reliability
    """

    def __init__(self):
        self.processes: Dict[str, subprocess.Process] = {}  # server_name -> process
        self.server_tools: Dict[str, List[Dict[str, Any]]] = {}  # server_name -> tools
        self.tool_to_server: Dict[str, str] = {}  # tool_name -> server_name
        self.available_tools: List[Dict[str, Any]] = []  # Azure OpenAI format
        self.next_id = 1  # JSON-RPC message ID counter
        self._initialized = False
    
    async def start(self):
        """
        Initialize MCP client connections to all configured servers
        Raises exception if any server fails to connect (fail-fast approach)
        """
        if self._initialized:
            logger.warning("MCP client already initialized")
            return

        logger.info("Starting MCP client manager...")

        # Get the cdm-agent directory
        cdm_agent_dir = Path(__file__).parent.parent.resolve()

        # Define MCP servers to connect to
        servers_config = [
            {
                "name": "cdm-db",
                "script_path": cdm_agent_dir / "providers" / "cdm_db" / "provider.py",
                "description": "CDM Database provider for trade states, lineage, and diffs"
            },
            {
                "name": "cdm-ref",
                "script_path": cdm_agent_dir / "providers" / "cdm_ref" / "provider.py",
                "description": "CDM Reference provider for type definitions and validation"
            }
        ]

        # Connect to each server
        for config in servers_config:
            server_name = config["name"]
            script_path = config["script_path"]

            logger.info(f"Connecting to MCP server: {server_name} ({script_path})")

            try:
                process = await self._start_server_process(server_name, script_path)
                self.processes[server_name] = process
                logger.info(f"✅ Started {server_name} MCP server process")

                # Initialize the server
                await self._initialize_server(server_name)
                logger.info(f"✅ Initialized {server_name} MCP server")

            except Exception as e:
                logger.error(f"❌ Failed to connect to {server_name} MCP server: {e}")
                # Fail fast - cleanup and raise
                await self.shutdown()
                raise RuntimeError(f"Failed to connect to MCP server '{server_name}': {e}")

        # Discover tools from all servers
        await self._discover_all_tools()

        self._initialized = True
        logger.info(f"✅ MCP client initialized with {len(self.processes)} servers and {len(self.available_tools)} tools")
    
    async def _start_server_process(self, server_name: str, script_path: Path) -> subprocess.Process:
        """
        Start an MCP server process
        """
        if not script_path.exists():
            raise FileNotFoundError(f"MCP server script not found: {script_path}")

        logger.info(f"  → Spawning MCP server process: {sys.executable} {script_path}")

        # Start the process
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(script_path),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()
        )

        logger.info(f"  → Process started with PID: {process.pid}")
        return process

    async def _initialize_server(self, server_name: str):
        """
        Send initialize request to server and verify response
        """
        logger.info(f"  → Initializing MCP server: {server_name}")

        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": self.next_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "cdm-trade-insight",
                    "version": "1.0.0"
                }
            }
        }
        self.next_id += 1

        response = await self._send_request(server_name, init_request)

        if "error" in response:
            raise RuntimeError(f"Server initialization failed: {response['error']}")

        logger.info(f"  → Server initialized: {response['result']['serverInfo']['name']}")

    async def _send_request(self, server_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to a server and get response
        """
        process = self.processes.get(server_name)
        if not process:
            raise RuntimeError(f"No process for server {server_name}")

        # Send request
        request_json = json.dumps(request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()

        # Read response
        response_line = await process.stdout.readline()
        response = json.loads(response_line.decode().strip())

        return response
    
    async def _discover_all_tools(self):
        """
        Discover tools from all connected MCP servers and convert to Azure OpenAI format
        """
        logger.info("Discovering tools from all MCP servers...")

        for server_name in self.processes.keys():
            try:
                # Send tools/list request
                list_request = {
                    "jsonrpc": "2.0",
                    "id": self.next_id,
                    "method": "tools/list",
                    "params": {}
                }
                self.next_id += 1

                response = await self._send_request(server_name, list_request)

                if "error" in response:
                    raise RuntimeError(f"Tool discovery failed: {response['error']}")

                server_tools = []

                # Convert each MCP tool to Azure OpenAI function calling format
                for tool in response["result"]["tools"]:
                    azure_tool = {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool["inputSchema"]
                        }
                    }

                    server_tools.append(azure_tool)
                    self.available_tools.append(azure_tool)
                    self.tool_to_server[tool["name"]] = server_name

                    logger.debug(f"  - {server_name}: {tool['name']}")

                self.server_tools[server_name] = server_tools
                logger.info(f"Discovered {len(server_tools)} tools from {server_name}")

            except Exception as e:
                logger.error(f"Failed to discover tools from {server_name}: {e}")
                raise
        
        logger.info(f"Total tools discovered: {len(self.available_tools)}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool by name with given arguments
        Routes the call to the appropriate MCP server

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as dict

        Returns:
            Tool result (parsed from MCP response)

        Raises:
            ValueError: If tool not found
            RuntimeError: If tool call fails
        """
        if not self._initialized:
            raise RuntimeError("MCP client not initialized. Call start() first.")

        # Find which server has this tool
        server_name = self.tool_to_server.get(tool_name)

        if not server_name:
            available_tools = ", ".join(self.tool_to_server.keys())
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")

        try:
            # Send tools/call request
            call_request = {
                "jsonrpc": "2.0",
                "id": self.next_id,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            self.next_id += 1

            logger.debug(f"Calling tool '{tool_name}' on server '{server_name}' with args: {arguments}")
            response = await self._send_request(server_name, call_request)

            if "error" in response:
                raise RuntimeError(f"Tool call failed: {response['error']}")

            # Parse MCP response
            # MCP returns result with content array
            content = response["result"]["content"]
            if content and len(content) > 0:
                # Get the first content item (usually text)
                content_item = content[0]
                if content_item["type"] == "text":
                    text = content_item["text"]
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        # Return as-is if not JSON
                        return text
                else:
                    # Return the content item as-is
                    return content_item

            # Empty result
            return {}

        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}' on server '{server_name}': {e}")
            raise RuntimeError(f"Tool call failed: {e}")
    
    async def shutdown(self):
        """
        Clean up all MCP connections
        """
        logger.info("Shutting down MCP client manager...")

        for server_name, process in self.processes.items():
            try:
                logger.debug(f"Terminating process for {server_name}")
                # Terminate the process
                process.terminate()

                # Wait for it to finish
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                    logger.debug(f"Process {server_name} terminated cleanly")
                except asyncio.TimeoutError:
                    logger.warning(f"Process {server_name} didn't terminate cleanly, killing...")
                    process.kill()
                    await process.wait()

            except Exception as e:
                logger.error(f"Error terminating {server_name}: {e}")

        self.processes.clear()
        self.server_tools.clear()
        self.tool_to_server.clear()
        self.available_tools.clear()
        self._initialized = False

        logger.info("MCP client manager shut down")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get all available tools in Azure OpenAI function calling format
        """
        if not self._initialized:
            raise RuntimeError("MCP client not initialized. Call start() first.")
        return self.available_tools
    
    def is_initialized(self) -> bool:
        """
        Check if the MCP client is initialized and ready
        """
        return self._initialized

