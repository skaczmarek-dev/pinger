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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg: #f5f5f5;
            --card: #ffffff;
            --text: #333333;
            --th-bg: #4CAF50;
            --th-color: #ffffff;
            --toggle-border: rgba(0,0,0,0.08);
            --toggle-bg: rgba(255,255,255,0.6);
            --toggle-color: var(--text);
        }
        .dark-theme {
            --bg: #0f1720;
            --card: #0b1220;
            --text: #e5e7eb;
            --th-bg: #0ea5a3;
            --th-color: #062023;
            --toggle-border: rgba(255,255,255,0.12);
            --toggle-bg: rgba(255,255,255,0.04);
            --toggle-color: var(--text);
        }
        html, body { height: 100%; }
        body { font-family: Arial; margin: 40px; background: var(--bg); color: var(--text); }
        h1 { color: var(--text); }
        table { border-collapse: collapse; width: 100%; background: var(--card); }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: var(--th-bg); color: var(--th-color); }
        .up { color: #22c55e; font-weight: bold; }
        .down { color: #ef4444; font-weight: bold; }
        /* Theme toggle button */
        #theme-toggle { background: var(--toggle-bg); border: 1px solid var(--toggle-border); color: var(--toggle-color); padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size:16px; line-height:1; }
        #theme-toggle:hover { opacity: 0.95; }
    </style>
</head>
<body>
    <div style="position:fixed; top:12px; right:12px; z-index:999">
        <button id="theme-toggle" aria-label="Toggle theme"><i id="theme-icon" class="fa-solid fa-moon"></i></button>
    </div>
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

# Add small JS to handle theme toggle and remember choice in localStorage
HTML_TEMPLATE = HTML_TEMPLATE.replace("</body>\n</html>\n", """<script>
    (function(){
        const toggle = document.getElementById('theme-toggle');
        if(!toggle) return;
        const icon = document.getElementById('theme-icon');
        const apply = (theme)=>{
            if(theme==='dark') document.documentElement.classList.add('dark-theme');
            else document.documentElement.classList.remove('dark-theme');
            if(icon){
                icon.className = theme==='dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
            }
        };
        let stored = localStorage.getItem('theme');
        if(!stored){
            stored = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
        }
        apply(stored);
        toggle.addEventListener('click', function(){
            const newt = document.documentElement.classList.contains('dark-theme') ? 'light' : 'dark';
            localStorage.setItem('theme', newt);
            apply(newt);
        });
    })();
    </script>
</body>
</html>
""")

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
