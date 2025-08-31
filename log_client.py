import socket
import sys
import time
import threading

class LogClient:
    def __init__(self, server_host, server_port=18194):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.running = False
        
        # Heartbeat configuration
        self.heartbeat_timeout = 5
        self.last_heartbeat = 0
        self.heartbeat_lock = threading.Lock()

    def connect(self, retry_delay=1, max_retries=None):
        """
        Connect to the log server with retry logic.
        
        Args:
            retry_delay: Seconds to wait between retry attempts
            max_retries: Maximum number of retries (None for infinite)
        """
        attempt = 0
        
        while True:
            attempt += 1
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.socket.settimeout(3.0)  # Timeout for server response
                
                register_msg = "REGISTER"
                self.socket.sendto(register_msg.encode('utf-8'), (self.server_host, self.server_port))
                
                # Wait for server response (cached messages or any response)
                try:
                    data, addr = self.socket.recvfrom(4096)
                    print("=" * 50)
                    
                    # Process the first message we received
                    message = data.decode('utf-8')
                    sys.stdout.write(message)
                    sys.stdout.flush()
                    
                    self.socket.settimeout(1.0)  # Reset to normal timeout for listening
                    self.running = True
                    
                    # Initialize heartbeat tracking
                    with self.heartbeat_lock:
                        self.last_heartbeat = time.time()
                    
                    return True
                    
                except socket.timeout:
                    # No response from server - server not available
                    raise Exception("No response from server")
                
            except Exception as e:
                if self.socket:
                    self.socket.close()
                    self.socket = None
                
                if attempt == 1:
                    print("Waiting server to show up...")
                
                # Check if we should stop retrying
                if max_retries is not None and attempt >= max_retries:
                    print("Maximum retry attempts reached. Giving up.")
                    return False
                try:
                    time.sleep(retry_delay)
                except KeyboardInterrupt:
                    print("\nConnection retry interrupted by user")
                    return False

    def send_heartbeat_ack(self):
        """Send heartbeat acknowledgment to server"""
        try:
            if self.socket and self.running:
                ack_msg = "HEARTBEAT_ACK"
                self.socket.sendto(ack_msg.encode('utf-8'), (self.server_host, self.server_port))
        except Exception as e:
            # If we can't send heartbeat ack, we'll detect this in the main loop
            pass

    def is_server_alive(self):
        """Check if we've received a heartbeat from server recently"""
        with self.heartbeat_lock:
            return (time.time() - self.last_heartbeat) < self.heartbeat_timeout

    def listen(self):
        buffer_size = 4096
        message_buffer = ""  # Buffer to assemble chunked messages
        
        while self.running:
            try:
                # Check if server is still alive (heartbeat check)
                if not self.is_server_alive():
                    print("=" * 50)
                    print("Server heartbeat timeout, attempting to reconnect...")
                    raise Exception("Server heartbeat timeout")
                
                # Receive message
                data, addr = self.socket.recvfrom(buffer_size)
                message = data.decode('utf-8').strip()
                
                # Handle heartbeat messages
                if message == "HEARTBEAT":
                    with self.heartbeat_lock:
                        self.last_heartbeat = time.time()
                    self.send_heartbeat_ack()
                    continue
                
                # Handle end-of-message marker for chunked messages
                if message == "<<EOM>>":
                    # Complete message assembled, print it
                    if message_buffer:
                        sys.stdout.write(message_buffer)
                        sys.stdout.flush()
                        message_buffer = ""
                    continue
                
                # Handle regular messages (update heartbeat time for any server communication)
                with self.heartbeat_lock:
                    self.last_heartbeat = time.time()
                
                # Check if this might be a chunked message or a complete message
                if len(data) >= 1024:
                    # This might be a chunk of a larger message, buffer it
                    message_buffer += message
                else:
                    # This is likely a complete message, print immediately
                    if message_buffer:
                        # We had buffered content, this completes it
                        message_buffer += message
                        sys.stdout.write(message_buffer)
                        sys.stdout.flush()
                        message_buffer = ""
                    else:
                        # Single complete message
                        if not message.endswith('\n'):
                            message += '\n'
                        sys.stdout.write(message)
                        sys.stdout.flush()
                
            except socket.timeout:
                # Timeout is normal, continue listening but check heartbeat
                continue
            except Exception as e:
                if self.running:
                    print("Connection lost")
                    
                    # Try to reconnect
                    if self.socket:
                        self.socket.close()
                        self.socket = None
                    
                    if not self.connect():
                        print("Failed to reconnect. Exiting.")
                        break

    def disconnect(self):
        self.running = False
        if self.socket:
            self.socket.close()
        print("\nDisconnected from log server")

def print_usage():
    print("Usage: python log_client.py <server_host> [server_port]")
    print("  server_host: IP address or hostname of the log server (required)")
    print("  server_port: Port number (default: 18194)")
    print("")
    print("Examples:")
    print("  python log_client.py 192.168.1.100")
    print("  python log_client.py 192.168.1.100 18194")

def main():
    # Check if server_host is provided
    if len(sys.argv) < 2:
        print("Error: server_host is required")
        print_usage()
        sys.exit(1)
    
    # Parse command line arguments
    server_host = sys.argv[1]
    server_port = 18194
    
    if len(sys.argv) > 2:
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print("Error: server_port must be a valid integer")
            print_usage()
            sys.exit(1)
    
    # Create and connect client
    client = LogClient(server_host, server_port)
    
    if not client.connect():
        sys.exit(1)
    
    try:
        # Listen for log messages
        client.listen()
    except KeyboardInterrupt:
        print("\nReceived Ctrl+C, shutting down...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()