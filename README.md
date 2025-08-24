# BItChat - Bluetooth Mesh Chat Application

A peer-to-peer chat application that uses Bluetooth mesh networking to enable communication when the internet is unavailable.

## Features

- **Bluetooth Mesh Networking**: Messages are routed through a mesh network of connected devices
- **Peer-to-Peer Communication**: Direct messaging between users without central servers
- **Broadcast Messaging**: Send messages to all connected peers in the network
- **Automatic Route Discovery**: Dynamic routing table updates based on network topology
- **Offline Capability**: Works without internet connectivity
- **Real-time Chat Interface**: Modern GUI with message history and peer status

## Architecture

### Server Component (`server.py`)
- **Mesh Network Coordinator**: Manages the Bluetooth mesh network
- **Message Routing**: Routes messages through the mesh using distance vector routing
- **Peer Management**: Handles peer registration, discovery, and connectivity monitoring
- **Message Types**: Supports text messages, system messages, route updates, and acknowledgments

### Client Component (`mesh_client.py`)
- **User Interface**: Tkinter-based GUI for sending and receiving messages
- **Network Integration**: Connects to the mesh network and participates in message routing
- **Peer Discovery**: Automatically discovers and displays connected peers
- **Message Handling**: Processes incoming messages and displays them in real-time

## Key Components

### Message Types
- `TEXT`: Regular chat messages
- `SYSTEM`: System notifications and status updates
- `ROUTE_UPDATE`: Network topology updates
- `PEER_DISCOVERY`: Peer discovery and registration
- `ACK`: Message acknowledgments

### Routing Algorithm
The application uses a simplified distance vector routing algorithm:
- Each node maintains a routing table with costs to destinations
- Routes are updated based on neighbor information
- Messages are forwarded to the next hop with lowest cost
- TTL (Time To Live) prevents infinite message loops

### Mesh Network Features
- **Automatic Peer Discovery**: New peers are automatically discovered and registered
- **Dynamic Routing**: Routes are updated as network topology changes
- **Fault Tolerance**: Network continues to function even if some peers disconnect
- **Message Reliability**: Acknowledgments ensure message delivery

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- Bluetooth-capable device (for real implementation)
- tkinter (usually included with Python)

### Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd BItChat
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

#### Start the Server
```bash
python server.py
```

#### Start the Client
```bash
python mesh_client.py
```

## Usage

### Server Operation
1. The server starts automatically and begins listening for peer connections
2. It manages the mesh network topology and routes messages
3. Monitor the console output for network status and message routing information

### Client Operation
1. Launch the client application
2. Click "Connect" to join the mesh network
3. Send messages using the text input field
4. View connected peers in the Network Information section
5. Click "Disconnect" to leave the network

## Network Topology

```
Peer A -------- Peer B -------- Peer C
   |              |              |
   |              |              |
Peer D -------- Peer E -------- Peer F
```

Messages can be routed through multiple hops to reach their destination:
- Direct messages: A → B
- Multi-hop messages: A → B → C → F

## Implementation Notes

### Current Implementation
The current version simulates Bluetooth mesh networking. In a real implementation, you would need to:

1. **Bluetooth Integration**: Use Bluetooth libraries (e.g., `pybluez`, `bleak`) for actual Bluetooth communication
2. **Mesh Protocol**: Implement Bluetooth mesh networking protocols
3. **Device Discovery**: Use Bluetooth device discovery and pairing
4. **Security**: Implement encryption and authentication for secure communication

### Bluetooth Mesh Considerations
- **Range**: Bluetooth mesh typically has a range of 10-100 meters
- **Battery Life**: Mesh networking can be power-intensive
- **Interference**: Other Bluetooth devices may cause interference
- **Regulatory**: Ensure compliance with local Bluetooth regulations

## Future Enhancements

1. **Real Bluetooth Integration**: Replace simulation with actual Bluetooth mesh networking
2. **Message Encryption**: End-to-end encryption for secure communication
3. **File Sharing**: Support for sharing files through the mesh network
4. **Voice Messages**: Audio message support
5. **Group Chats**: Dedicated group chat functionality
6. **Message Persistence**: Local message storage and history
7. **Network Visualization**: Visual representation of the mesh network topology

## Troubleshooting

### Common Issues
1. **Connection Problems**: Ensure Bluetooth is enabled and devices are in range
2. **Message Delivery**: Check if the destination peer is online and reachable
3. **Network Performance**: Large networks may experience routing delays

### Debug Mode
Enable debug logging by modifying the logging level in both server.py and mesh_client.py:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bluetooth SIG for mesh networking specifications
- Python community for excellent libraries and tools
- Open source community for inspiration and best practices
