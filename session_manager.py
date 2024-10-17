import docker
from flask import Flask, request, jsonify, render_template
import time
import os
import threading
import logging
import json
from selenium.common.exceptions import WebDriverException
from fieldnation_script import FieldNationAutomation
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

HOST_IP = os.getenv('HOST_IP') or 'localhost'

# Add these lines at the beginning of the file, after the imports
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder=os.path.abspath('templates'))
client = docker.from_env()


DOCKER_NETWORK = os.environ.get('DOCKER_NETWORK', 'session-network')

PORT_POOL_START = 7900
PORT_POOL_SIZE = 100
port_pool = list(range(PORT_POOL_START, PORT_POOL_START + PORT_POOL_SIZE))

customData: Dict[str, Dict[str, Any]] = {
    "user1": {"email": None, "data": None, "automation": None},
    "user2": {"email": None, "data": None, "automation": None},
    "user3": {"email": None, "data": None, "automation": None},
}

users = {
    "user1": {"password": "pass1", "container_name": None, "vnc_port": None, "session_active": False, "automation_running": False, "stop_event": None},
    "user2": {"password": "pass2", "container_name": None, "vnc_port": None, "session_active": False, "automation_running": False, "stop_event": None},
    "user3": {"password": "pass3", "container_name": None, "vnc_port": None, "session_active": False, "automation_running": False, "stop_event": None},
}

for i, (user_id, user_data) in enumerate(users.items()):
    users[user_id]['assigned_port'] = port_pool[i]

def create_chrome_container(user_id):
    container_name = f"chrome-{user_id}"
    volume_name = f"{user_id}-profile-data"
    assigned_port = users[user_id]['assigned_port']

    try:
        existing_container = client.containers.get(container_name)
        logger.info(f"Container {container_name} already exists")
        
        if existing_container.status != "running":
            logger.info(f"Starting existing container {container_name}")
            existing_container.start()
        
        time.sleep(2)
        
        existing_container.reload()
        vnc_port = existing_container.ports.get('7900/tcp')
        
        if not vnc_port:
            logger.info(f"No port mapping found for {container_name}. Recreating the container.")
            existing_container.remove(force=True)
            raise docker.errors.NotFound("Container exists but has no port mapping")
        
        vnc_port = vnc_port[0]['HostPort']
        return container_name, vnc_port

    except docker.errors.NotFound:
        logger.info(f"Container {container_name} not found or removed, creating a new one")
    
    try:
        logger.info(f"Checking if volume {volume_name} exists")
        volume = client.volumes.get(volume_name)
    except docker.errors.NotFound:
        logger.info(f"Volume {volume_name} not found, creating it")
        volume = client.volumes.create(name=volume_name, driver='local')

    try:
        container = client.containers.run(
            "selenium/standalone-chrome:latest",
            name=container_name,
            detach=True, 
            environment=[
                f"VNC_PASSWORD={users[user_id]['password']}",
                "SCREEN_WIDTH=1920",
                "SCREEN_HEIGHT=1080",
            ],
            network=DOCKER_NETWORK,
            ports={'7900/tcp': assigned_port},  
            volumes={volume_name: {'bind': '/home/seluser/chrome-profile', 'mode': 'rw'}},
        )
        time.sleep(2)
        container = client.containers.get(container_name)
        vnc_port = assigned_port  
        container.exec_run("sudo chown -R seluser:seluser /home/seluser/chrome-profile")
        container.exec_run("chmod -R 700 /home/seluser/chrome-profile")
        container.exec_run("rm -rf /home/seluser/chrome-profile/SingletonLock")
        container.exec_run("rm -rf /home/seluser/chrome-profile/SingletonSocket")
        container.exec_run("rm -rf /home/seluser/chrome-profile/Cache/*")
        logger.info(f"Container {container_name} created successfully")
        logger.info(f"VNC port for container {container_name}: {vnc_port}")
        
        return container_name, vnc_port
    except Exception as e:
        logger.error(f"Error creating container: {str(e)}")
        raise

def start_automation(user_id):
    try:
        stop_event = threading.Event()
        users[user_id]['stop_event'] = stop_event
        users[user_id]['automation_running'] = True
        field_nation_script = FieldNationAutomation(user_id, customData[user_id])
        field_nation_script.run(stop_event)
    except WebDriverException as e:
        logger.error(f"WebDriver error for {user_id}: {str(e)}")
        users[user_id]['automation_running'] = False
    except Exception as e:
        logger.error(f"Error in automation for {user_id}: {str(e)}")
    finally:
        logger.info(f"Automation stopped for {user_id}")
        users[user_id]['automation_running'] = False
        users[user_id]['stop_event'] = None

@app.route('/')
def index():
    custom_data_fields = list(next(iter(customData.values())).keys())
    return render_template('index.html', users=json.dumps(list(users.keys())), custom_data_fields=json.dumps(custom_data_fields))

@app.route('/get_session_status', methods=['GET'])
def get_session_status():
    return jsonify({user_id: {"session_active": user['session_active'], "automation_running": user['automation_running']} for user_id, user in users.items()})

@app.route('/create_session', methods=['POST'])
def create_session():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')
    
    if user_id not in users or users[user_id]['password'] != password:
        return jsonify({"error": "Invalid user_id or password"}), 401
    
    if users[user_id]['container_name'] is None:
        container_name, vnc_port = create_chrome_container(user_id)
        users[user_id]['container_name'] = container_name
        users[user_id]['vnc_port'] = vnc_port
        users[user_id]['session_active'] = True
    
    return jsonify({
        'user_id': user_id,
        'vnc_url': f'http://{HOST_IP}:{users[user_id]["assigned_port"]}',
        'container_name': users[user_id]['container_name'],
        'session_active': users[user_id]['session_active'],
        'automation_running': users[user_id]['automation_running']
    })



@app.route('/start_automation/<user_id>', methods=['POST'])
def start_automation_route(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    
    if not users[user_id]['session_active']:
        return jsonify({"error": "No active session found"}), 400
    
    if users[user_id]['automation_running']:
        return jsonify({"error": "Automation is already running"}), 400
    
    # Get custom data from request
    custom_data = request.json.get('customData', {})
    
    # Update customData for the user
    customData[user_id].update(custom_data)
    
    users[user_id]['automation_running'] = True
    threading.Thread(target=start_automation, args=(user_id,)).start()
    
    return jsonify({"status": "success", "message": f"Automation started for {user_id}"})

@app.route('/stop_automation/<user_id>', methods=['POST'])
def stop_automation(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    
    if not users[user_id]['automation_running']:
        return jsonify({"error": "Automation is not running"}), 400
    
    if users[user_id]['stop_event']:
        users[user_id]['stop_event'].set()
    
    users[user_id]['automation_running'] = False
    return jsonify({"status": "success", "message": f"Automation stopped for {user_id}"})

@app.route('/end_session/<user_id>', methods=['POST'])
def end_session(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    
    container_name = users[user_id]['container_name']
    volume_name = f"{user_id}-profile-data"
    
    if container_name:
        try:
            # Stop and remove the container
            container = client.containers.get(container_name)
            container.stop()
            container.remove()
            
            # Log that we're keeping the volume
            logger.info(f"Keeping volume {volume_name} for future sessions")
            
            # Reset user session data
            users[user_id]['container_name'] = None
            users[user_id]['vnc_port'] = None
            users[user_id]['session_active'] = False
            users[user_id]['automation_running'] = False
            
            return jsonify({"status": "success", "message": f"Session ended for {user_id}. Volume kept for future use."})
        except docker.errors.NotFound:
            return jsonify({"error": "Container not found"}), 404
        except Exception as e:
            logger.error(f"Error ending session for {user_id}: {str(e)}")
            return jsonify({"error": "An error occurred while ending the session"}), 500
    else:
        return jsonify({"error": "No active session found"}), 404

@app.route('/get_vnc_url/<user_id>', methods=['GET'])
def get_vnc_url(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    
    if not users[user_id]['session_active']:
        return jsonify({"error": "No active session found"}), 400
    
    vnc_port = users[user_id]['vnc_port']
    return jsonify({"vnc_url": f"http://{HOST_IP}:{vnc_port}"})

@app.route('/get_custom_data_fields', methods=['GET'])
def get_custom_data_fields():
    # Assuming all users have the same custom data fields
    sample_user = next(iter(customData.values()))
    return jsonify(list(sample_user.keys()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
