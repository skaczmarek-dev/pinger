from flask import Flask, render_template_string
import subprocess
import threading
import time
import os

app = Flask(__name__)

# Server status dictionary
server_status = {}

def ping_host(host):
    """Ping a host and return True if it responds"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error pinging {host}: {e}")
        return False

def check_servers():
    """Background function to check servers from list"""
    hosts_file = os.getenv('HOSTS_FILE', '/app/config/hosts.txt')
    interval = int(os.getenv('CHECK_INTERVAL', '30'))
    
    while True:
        try:
            with open(hosts_file, 'r') as f:
                hosts = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            # Remove hosts that are no longer present in the file
            current_hosts = set(hosts)
            for old in list(server_status.keys()):
                if old not in current_hosts:
                    del server_status[old]

            for host in hosts:
                status = ping_host(host)
                server_status[host] = {
                    'status': 'UP' if status else 'DOWN',
                    'last_check': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                print(f"{host}: {'UP' if status else 'DOWN'}")
        
        except FileNotFoundError:
            print(f"File {hosts_file} not found")
        
        time.sleep(interval)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Server Pinger</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial; margin: 40px; background: #f5f5f5; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; background: white; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #1F10E3; color: white; }
        .up { color: green; font-weight: bold; }
        .down { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>📡 Server Status Monitor</h1>
    <p>Auto-refresh every 10s | Check interval: {{ interval }}s</p>
    <table>
        <tr>
            <th>Host</th>
            <th>Status</th>
            <th>Last Check</th>
        </tr>
        {% for host, data in servers.items() %}
        <tr>
            <td>{{ host }}</td>
            <td class="{{ data.status|lower }}">{{ data.status }}</td>
            <td>{{ data.last_check }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    interval = os.getenv('CHECK_INTERVAL', '30')
    return render_template_string(HTML_TEMPLATE, servers=server_status, interval=interval)

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    # Start background checker thread
    checker = threading.Thread(target=check_servers, daemon=True)
    checker.start()
    
    # Start Flask
    app.run(host='0.0.0.0', port=5000)
