import httpx
import re
import random
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- CONFIGURATION ---
# Proxy format: http://username:password@ip:port
# Aap yahan apni proxies ki list daal sakte hain
PROXIES = [
    "http://user1:pass1@ip1:port1",
    "http://user2:pass2@ip2:port2",
    "http://user3:pass3@ip3:port3"
]

UA = "Mozilla/5.0 (Linux; Android 12; LAVA Blaze Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.116 Mobile Safari/537.36"

def inject_views_with_rotation(target_url):
    match = re.search(r'reel/([^/?]+)', target_url)
    reel_id = match.group(1) if match else None
    if not reel_id: return {"success": "Invalid Link"}
    
    clean_url = f"https://www.instagram.com/reel/{reel_id}/"
    
    # 1. Random IP Select karna (Rotation)
    selected_proxy = random.choice(PROXIES) if PROXIES else None
    proxy_config = {"all://": selected_proxy} if selected_proxy else None

    headers = {
        "host": "leofame.com",
        "user-agent": UA,
        "content-type": "application/x-www-form-urlencoded",
        "x-requested-with": "mark.via.gp",
        "referer": "https://leofame.com/free-instagram-views",
    }

    # 2. HTTP/2 with Proxy Support
    with httpx.Client(http2=True, proxies=proxy_config, timeout=30.0) as client:
        try:
            # Step 1: Handshake
            r1 = client.get("https://leofame.com/free-instagram-views")
            token = client.cookies.get("token")
            
            if not token:
                return {"success": "IP Blocked or Token Failed"}

            # Step 2: Inject
            payload = {
                "token": token,
                "timezone_offset": "Asia/Calcutta",
                "free_link": clean_url,
                "quantity": "200"
            }

            r2 = client.post("https://leofame.com/free-instagram-views?api=1", data=payload, headers=headers)
            
            # Response ke saath IP info bhi bhejenge debugging ke liye
            res_json = r2.json()
            res_json['used_proxy'] = selected_proxy if selected_proxy else "Server Default"
            return res_json
            
        except Exception as e:
            return {"success": f"Error: {str(e)}"}

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leofame Advanced Bot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    </head>
    <body class="bg-[#050505] text-white flex items-center justify-center min-h-screen">
        <div class="w-full max-w-md p-8 bg-[#111] rounded-3xl border border-zinc-800 shadow-2xl text-center">
            <h1 class="text-3xl font-black text-blue-500 mb-2">ULTRA BOT 🚀</h1>
            <p class="text-zinc-500 text-xs mb-8">Auto IP Rotation & HTTP/2 Active</p>
            
            <input type="text" id="url" placeholder="Enter Instagram Link" 
                   class="w-full p-4 bg-black rounded-2xl border border-zinc-800 mb-4 outline-none focus:border-blue-500 transition">
            
            <button id="go" class="w-full bg-blue-600 p-4 rounded-2xl font-bold hover:bg-blue-500 active:scale-95 transition">
                Start Injection
            </button>
            
            <div id="res" class="mt-8 hidden p-5 rounded-2xl text-sm font-mono text-left bg-black border border-zinc-800">
                <p id="status"></p>
                <p id="proxy_info" class="text-[10px] text-zinc-600 mt-2"></p>
            </div>
        </div>
        <script>
            $('#go').click(function(){
                const url = $('#url').val();
                const btn = $(this);
                btn.prop('disabled', true).text('Rotating IP...');
                
                $.getJSON('/api?url=' + encodeURIComponent(url), function(data){
                    $('#res').removeClass('hidden');
                    $('#status').text("Result: " + data.success).css('color', data.success == "Success" ? "#4ade80" : "#f87171");
                    $('#proxy_info').text("Used Proxy: " + data.used_proxy);
                    btn.prop('disabled', false).text('Start Injection');
                });
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/api')
def api():
    url = request.args.get('url')
    return jsonify(inject_views_with_rotation(url))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
