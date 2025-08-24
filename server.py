import asyncio
import json
import uuid
import time
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    TEXT = "text"
    SYSTEM = "system"
    ROUTE_UPDATE = "route_update"
    PEER_DISCOVERY = "peer_discovery"
    ACK = "acknowledgment"

@dataclass
class Message:
    id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast messages
    message_type: MessageType
    content: str
    timestamp: float
    ttl: int = 10  # Time to live for message routing
    route: List[str] = None  # Path taken by message through mesh

@dataclass
class Peer:
    id: str
    name: str
    address: str
    last_seen: float
    is_online: bool = True
    neighbors: Set[str] = None  # Connected peer IDs

class BluetoothMeshChatServer:
    def __init__(self, server_id: str = None, server_name: str = "MeshServer"):
        self.server_id = server_id or str(uuid.uuid4())
        self.server_name = server_name
        self.peers: Dict[str, Peer] = {}
        self.messages: Dict[str, Message] = {}
        self.routing_table: Dict[str, Dict[str, str]] = {}  # destination -> {next_hop: cost}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        
        # Add self to peers
        self.peers[self.server_id] = Peer(
            id=self.server_id,
            name=self.server_name,
            address="localhost",
            last_seen=time.time(),
            neighbors=set()
        )
        
        logger.info(f"Bluetooth Mesh Chat Server initialized with ID: {self.server_id}")
    
    async def start(self):
        """Start the mesh server"""
        self.running = True
        logger.info("Starting Bluetooth Mesh Chat Server...")
        
        # Start background tasks
        asyncio.create_task(self._message_processor())
        asyncio.create_task(self._peer_monitor())
        asyncio.create_task(self._route_updater())
        
        logger.info("Bluetooth Mesh Chat Server started successfully")
    
    async def stop(self):
        """Stop the mesh server"""
        self.running = False
        logger.info("Bluetooth Mesh Chat Server stopped")
    
    async def register_peer(self, peer_id: str, peer_name: str, address: str) -> bool:
        """Register a new peer in the mesh network"""
        if peer_id in self.peers:
            # Update existing peer
            self.peers[peer_id].name = peer_name
            self.peers[peer_id].address = address
            self.peers[peer_id].last_seen = time.time()
            self.peers[peer_id].is_online = True
            logger.info(f"Updated peer: {peer_name} ({peer_id})")
        else:
            # Add new peer
            self.peers[peer_id] = Peer(
                id=peer_id,
                name=peer_name,
                address=address,
                last_seen=time.time(),
                neighbors=set()
            )
            logger.info(f"Registered new peer: {peer_name} ({peer_id})")
        
        # Send peer discovery message to all connected peers
        await self._broadcast_peer_discovery()
        return True
    
    async def unregister_peer(self, peer_id: str) -> bool:
        """Unregister a peer from the mesh network"""
        if peer_id in self.peers:
            self.peers[peer_id].is_online = False
            self.peers[peer_id].last_seen = time.time()
            logger.info(f"Unregistered peer: {self.peers[peer_id].name} ({peer_id})")
            
            # Update routing table
            await self._update_routing_table()
            return True
        return False
    
    async def send_message(self, sender_id: str, recipient_id: str, content: str) -> str:
        """Send a message to a specific peer"""
        message_id = str(uuid.uuid4())
        message = Message(
            id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.TEXT,
            content=content,
            timestamp=time.time(),
            route=[sender_id]
        )
        
        self.messages[message_id] = message
        await self.message_queue.put(message)
        logger.info(f"Message queued: {sender_id} -> {recipient_id}")
        return message_id
    
    async def broadcast_message(self, sender_id: str, content: str) -> str:
        """Broadcast a message to all peers in the mesh"""
        message_id = str(uuid.uuid4())
        message = Message(
            id=message_id,
            sender_id=sender_id,
            recipient_id=None,  # None for broadcast
            message_type=MessageType.TEXT,
            content=content,
            timestamp=time.time(),
            route=[sender_id]
        )
        
        self.messages[message_id] = message
        await self.message_queue.put(message)
        logger.info(f"Broadcast message queued: {sender_id}")
        return message_id
    
    async def _message_processor(self):
        """Background task to process and route messages"""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self._route_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in message processor: {e}")
    
    async def _route_message(self, message: Message):
        """Route a message through the mesh network"""
        if message.ttl <= 0:
            logger.warning(f"Message {message.id} TTL expired")
            return
        
        # Decrement TTL
        message.ttl -= 1
        
        if message.recipient_id is None:
            # Broadcast message
            await self._broadcast_to_neighbors(message)
        else:
            # Direct message
            if message.recipient_id == self.server_id:
                # Message is for this server
                await self._handle_incoming_message(message)
            else:
                # Route to next hop
                next_hop = self._get_next_hop(message.recipient_id)
                if next_hop:
                    await self._forward_message(message, next_hop)
                else:
                    logger.warning(f"No route found for message to {message.recipient_id}")
    
    async def _broadcast_to_neighbors(self, message: Message):
        """Broadcast message to all connected neighbors"""
        for peer_id in self.peers[self.server_id].neighbors:
            if self.peers[peer_id].is_online:
                await self._forward_message(message, peer_id)
    
    async def _forward_message(self, message: Message, next_hop: str):
        """Forward message to next hop in the route"""
        # In a real implementation, this would send via Bluetooth
        # For now, we'll simulate the forwarding
        logger.info(f"Forwarding message {message.id} to {next_hop}")
        
        # Add current server to route
        if self.server_id not in message.route:
            message.route.append(self.server_id)
        
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # In real implementation, send via Bluetooth mesh
        # await self._send_via_bluetooth(next_hop, message)
    
    async def _handle_incoming_message(self, message: Message):
        """Handle incoming message for this server"""
        logger.info(f"Received message from {message.sender_id}: {message.content}")
        
        # Send acknowledgment
        ack_message = Message(
            id=str(uuid.uuid4()),
            sender_id=self.server_id,
            recipient_id=message.sender_id,
            message_type=MessageType.ACK,
            content=f"ACK:{message.id}",
            timestamp=time.time(),
            route=[self.server_id]
        )
        
        # Route acknowledgment back
        next_hop = self._get_next_hop(message.sender_id)
        if next_hop:
            await self._forward_message(ack_message, next_hop)
    
    def _get_next_hop(self, destination: str) -> Optional[str]:
        """Get next hop for routing to destination"""
        if destination in self.routing_table:
            # Return the neighbor with lowest cost
            return min(self.routing_table[destination].items(), key=lambda x: x[1])[0]
        return None
    
    async def _update_routing_table(self):
        """Update routing table based on current network topology"""
        # Simple distance vector routing
        # In a real implementation, this would use more sophisticated routing algorithms
        
        # Initialize routing table
        for peer_id in self.peers:
            if peer_id != self.server_id:
                self.routing_table[peer_id] = {}
        
        # Direct neighbors have cost 1
        for neighbor_id in self.peers[self.server_id].neighbors:
            if self.peers[neighbor_id].is_online:
                self.routing_table[neighbor_id][neighbor_id] = 1
        
        # For other peers, find shortest path
        for peer_id in self.peers:
            if peer_id != self.server_id and peer_id not in self.peers[self.server_id].neighbors:
                # Find shortest path through neighbors
                min_cost = float('inf')
                best_neighbor = None
                
                for neighbor_id in self.peers[self.server_id].neighbors:
                    if self.peers[neighbor_id].is_online:
                        # In real implementation, query neighbor for cost to destination
                        cost = 2  # Simplified: assume cost 2 through any neighbor
                        if cost < min_cost:
                            min_cost = cost
                            best_neighbor = neighbor_id
                
                if best_neighbor:
                    self.routing_table[peer_id][best_neighbor] = min_cost
    
    async def _peer_monitor(self):
        """Monitor peer connectivity"""
        while self.running:
            current_time = time.time()
            timeout = 30  # 30 seconds timeout
            
            for peer_id, peer in self.peers.items():
                if peer_id != self.server_id and peer.is_online:
                    if current_time - peer.last_seen > timeout:
                        peer.is_online = False
                        logger.warning(f"Peer {peer.name} ({peer_id}) timed out")
                        await self._update_routing_table()
            
            await asyncio.sleep(10)  # Check every 10 seconds
    
    async def _route_updater(self):
        """Periodically update routing information"""
        while self.running:
            await self._update_routing_table()
            await asyncio.sleep(30)  # Update every 30 seconds
    
    async def _broadcast_peer_discovery(self):
        """Broadcast peer discovery message"""
        discovery_message = Message(
            id=str(uuid.uuid4()),
            sender_id=self.server_id,
            recipient_id=None,
            message_type=MessageType.PEER_DISCOVERY,
            content=json.dumps({
                "peers": [asdict(peer) for peer in self.peers.values()]
            }),
            timestamp=time.time(),
            route=[self.server_id]
        )
        
        await self.message_queue.put(discovery_message)
    
    def get_network_status(self) -> dict:
        """Get current network status"""
        return {
            "server_id": self.server_id,
            "server_name": self.server_name,
            "peers": {
                peer_id: {
                    "name": peer.name,
                    "address": peer.address,
                    "is_online": peer.is_online,
                    "last_seen": peer.last_seen,
                    "neighbors": list(peer.neighbors) if peer.neighbors else []
                }
                for peer_id, peer in self.peers.items()
            },
            "routing_table": self.routing_table,
            "message_count": len(self.messages)
        }

# Example usage and testing
async def main():
    """Example usage of the Bluetooth Mesh Chat Server"""
    server = BluetoothMeshChatServer(server_name="TestServer")
    await server.start()
    
    try:
        # Register some test peers
        await server.register_peer("peer1", "Alice", "192.168.1.101")
        await server.register_peer("peer2", "Bob", "192.168.1.102")
        await server.register_peer("peer3", "Charlie", "192.168.1.103")
        
        # Simulate some messages
        await server.send_message("peer1", "peer2", "Hello Bob!")
        await server.broadcast_message("peer1", "Hello everyone!")
        
        # Keep server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
