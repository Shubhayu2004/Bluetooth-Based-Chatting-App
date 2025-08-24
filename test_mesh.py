#!/usr/bin/env python3
"""
Test script for BItChat - Bluetooth Mesh Chat Application
This script demonstrates the basic functionality of the mesh network.
"""

import asyncio
import time
import logging
from server import BluetoothMeshChatServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mesh_network():
    """Test the mesh network functionality"""
    print("=== BItChat Mesh Network Test ===\n")
    
    # Create server
    server = BluetoothMeshChatServer(server_name="TestServer")
    await server.start()
    
    try:
        print("1. Registering test peers...")
        await server.register_peer("peer1", "Alice", "192.168.1.101")
        await server.register_peer("peer2", "Bob", "192.168.1.102")
        await server.register_peer("peer3", "Charlie", "192.168.1.103")
        
        # Wait a moment for registration
        await asyncio.sleep(1)
        
        print("2. Testing direct messaging...")
        await server.send_message("peer1", "peer2", "Hello Bob! How are you?")
        await asyncio.sleep(0.5)
        
        print("3. Testing broadcast messaging...")
        await server.broadcast_message("peer1", "Hello everyone! This is a test message.")
        await asyncio.sleep(0.5)
        
        print("4. Testing message from another peer...")
        await server.send_message("peer2", "peer1", "Hi Alice! I'm doing great, thanks!")
        await asyncio.sleep(0.5)
        
        print("5. Testing group conversation...")
        await server.send_message("peer3", "peer1", "Hey Alice, can you help me with something?")
        await asyncio.sleep(0.5)
        
        await server.send_message("peer1", "peer3", "Of course Charlie! What do you need?")
        await asyncio.sleep(0.5)
        
        print("6. Displaying network status...")
        status = server.get_network_status()
        print(f"Server ID: {status['server_id']}")
        print(f"Server Name: {status['server_name']}")
        print(f"Connected Peers: {len(status['peers'])}")
        print(f"Total Messages: {status['message_count']}")
        
        print("\n7. Peer Information:")
        for peer_id, peer_info in status['peers'].items():
            print(f"  - {peer_info['name']} ({peer_id}): {'Online' if peer_info['is_online'] else 'Offline'}")
        
        print("\n8. Routing Table:")
        for destination, routes in status['routing_table'].items():
            print(f"  To {destination}: {routes}")
        
        print("\n9. Simulating peer disconnection...")
        await server.unregister_peer("peer3")
        await asyncio.sleep(1)
        
        print("10. Final network status:")
        final_status = server.get_network_status()
        print(f"Connected Peers: {len([p for p in final_status['peers'].values() if p['is_online']])}")
        
        print("\n=== Test completed successfully! ===")
        
        # Keep server running for a bit to see all messages
        print("\nKeeping server running for 5 seconds to process messages...")
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    finally:
        await server.stop()
        print("Server stopped.")

async def test_message_routing():
    """Test message routing functionality"""
    print("\n=== Testing Message Routing ===\n")
    
    server = BluetoothMeshChatServer(server_name="RoutingTestServer")
    await server.start()
    
    try:
        # Create a more complex network topology
        peers = [
            ("peer1", "Alice", "192.168.1.101"),
            ("peer2", "Bob", "192.168.1.102"),
            ("peer3", "Charlie", "192.168.1.103"),
            ("peer4", "Diana", "192.168.1.104"),
            ("peer5", "Eve", "192.168.1.105")
        ]
        
        print("1. Creating network topology...")
        for peer_id, name, address in peers:
            await server.register_peer(peer_id, name, address)
            await asyncio.sleep(0.1)
        
        print("2. Testing multi-hop routing...")
        # Simulate a message that needs to be routed through multiple hops
        await server.send_message("peer1", "peer5", "This message should be routed through the mesh network")
        await asyncio.sleep(1)
        
        print("3. Testing broadcast with multiple recipients...")
        await server.broadcast_message("peer2", "Broadcast message to all peers in the mesh")
        await asyncio.sleep(1)
        
        print("4. Network topology:")
        status = server.get_network_status()
        print(f"Total peers: {len(status['peers'])}")
        print(f"Routing table entries: {len(status['routing_table'])}")
        
        print("\n=== Routing test completed! ===")
        
    except Exception as e:
        logger.error(f"Routing test failed: {e}")
        raise
    finally:
        await server.stop()

def main():
    """Run all tests"""
    print("Starting BItChat Mesh Network Tests...\n")
    
    try:
        # Run basic functionality test
        asyncio.run(test_mesh_network())
        
        # Run routing test
        asyncio.run(test_message_routing())
        
        print("\n🎉 All tests completed successfully!")
        print("\nTo run the full application:")
        print("1. Start the server: python server.py")
        print("2. Start the client: python mesh_client.py")
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        logger.exception("Test execution failed")

if __name__ == "__main__":
    main()
