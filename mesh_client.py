import asyncio
import json
import uuid
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BluetoothMeshChatClient:
    def __init__(self, client_name: str = "Anonymous"):
        self.client_id = str(uuid.uuid4())
        self.client_name = client_name
        self.connected = False
        self.messages = []
        self.peers = {}
        
        # Create GUI
        self.root = tk.Tk()
        self.setup_gui()
        
    def setup_gui(self):
        self.root.title(f"BItChat - {self.client_name}")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding=5)
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(conn_frame, text=f"Client ID: {self.client_id}").pack(anchor=tk.W)
        ttk.Label(conn_frame, text=f"Name: {self.client_name}").pack(anchor=tk.W)
        
        # Connection controls
        conn_controls = ttk.Frame(conn_frame)
        conn_controls.pack(fill=tk.X, pady=(5, 0))
        
        self.connect_btn = ttk.Button(conn_controls, text="Connect", command=self.connect)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(conn_controls, text="Disconnect", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(conn_frame, text="Status: Disconnected", foreground="red")
        self.status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Chat area
        chat_frame = ttk.LabelFrame(main_frame, text="Chat", padding=5)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.messages_text = scrolledtext.ScrolledText(chat_frame, height=20, wrap=tk.WORD)
        self.messages_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Message input
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)
        
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(input_frame, textvariable=self.message_var)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT)
        
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        # Network info
        info_frame = ttk.LabelFrame(main_frame, text="Network Information", padding=5)
        info_frame.pack(fill=tk.X)
        
        self.peers_text = scrolledtext.ScrolledText(info_frame, height=6, wrap=tk.WORD)
        self.peers_text.pack(fill=tk.X)
        
        self.update_peers_display()
        
    def connect(self):
        try:
            self.connected = True
            self.status_label.config(text="Status: Connected", foreground="green")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            
            threading.Thread(target=self._background_tasks, daemon=True).start()
            self.add_message("System", "Connected to mesh network", is_broadcast=True)
            logger.info("Connected to mesh network")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
    
    def disconnect(self):
        self.connected = False
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.add_message("System", "Disconnected from mesh network", is_broadcast=True)
        logger.info("Disconnected from mesh network")
    
    def send_message(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to the mesh network first")
            return
        
        content = self.message_var.get().strip()
        if not content:
            return
        
        try:
            self.add_message(self.client_name, content, is_broadcast=True)
            self.message_var.set("")
            logger.info(f"Message sent: {content}")
        except Exception as e:
            messagebox.showerror("Send Error", f"Failed to send message: {e}")
    
    def add_message(self, sender: str, content: str, is_broadcast: bool = False):
        message = {
            "id": str(uuid.uuid4()),
            "sender": sender,
            "content": content,
            "timestamp": time.time(),
            "is_broadcast": is_broadcast
        }
        self.messages.append(message)
        self.root.after(0, self._update_messages_display)
    
    def _update_messages_display(self):
        self.messages_text.delete(1.0, tk.END)
        
        for message in self.messages[-100:]:
            timestamp = time.strftime("%H:%M:%S", time.localtime(message["timestamp"]))
            prefix = "[BROADCAST]" if message["is_broadcast"] else "[DIRECT]"
            line = f"[{timestamp}] {prefix} {message['sender']}: {message['content']}\n"
            self.messages_text.insert(tk.END, line)
        
        self.messages_text.see(tk.END)
    
    def update_peers_display(self):
        self.peers_text.delete(1.0, tk.END)
        
        if not self.peers:
            self.peers_text.insert(tk.END, "No peers connected")
        else:
            for peer_id, peer_info in self.peers.items():
                status = "Online" if peer_info.get("is_online", False) else "Offline"
                line = f"{peer_info.get('name', 'Unknown')} ({peer_id}) - {status}\n"
                self.peers_text.insert(tk.END, line)
    
    def _background_tasks(self):
        while self.connected:
            try:
                time.sleep(2)
                
                # Simulate peer discovery
                if len(self.peers) < 3:
                    simulated_peers = {
                        "peer1": {"name": "Alice", "is_online": True},
                        "peer2": {"name": "Bob", "is_online": True},
                        "peer3": {"name": "Charlie", "is_online": False}
                    }
                    
                    for peer_id, peer_info in simulated_peers.items():
                        if peer_id not in self.peers:
                            self.peers[peer_id] = peer_info
                    
                    self.root.after(0, self.update_peers_display)
                
            except Exception as e:
                logger.error(f"Background task error: {e}")
    
    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Shutting down client...")
        finally:
            if self.connected:
                self.disconnect()

def main():
    client = BluetoothMeshChatClient(client_name="User")
    client.run()

if __name__ == "__main__":
    main()
