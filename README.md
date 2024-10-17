# Session Manager with Chrome Automation (MVP)


## Infrastructure Overview

The MVP system consists of the following components:

1. **Session Manager**: A Flask server that manages Chrome containers and handles user requests.
2. **Chrome Containers**: Docker containers running Chrome browsers, created and managed by the Session Manager.
3. **Web Interface**: A basic user interface for interacting with the Session Manager.
4. **NGINX**: A reverse proxy that handles incoming requests and routes them to the appropriate services.

## MVP Features

- Create and manage Chrome browser sessions in isolated Docker containers
- Start and stop basic automation scripts within these browser sessions
- Simple customizable data input for automation tasks
- VNC access to view and interact with the browser sessions

## How It Works

1. The Session Manager runs as a Flask server in a Docker container.
2. Users interact with the system through a simple web interface.
3. When a user creates a session, the Session Manager spins up a new Docker container running Chrome.
4. Users can start automation tasks, which run Selenium scripts in the Chrome containers.
5. Basic custom data can be passed to the automation scripts through the web interface.

## Main Components

- `session_manager.py`: The core Flask application that manages sessions and automation.
- `fieldnation_script.py`: An example automation script (to be customized for specific use cases).
- `automation_script.py`: A base class for automation scripts.
- `templates/index.html`: The basic web interface for user interactions.
- `docker-compose.yaml`: Defines the Docker services for the application.

## Usage

1. **Create Session**: Click "Create Session" and enter the password for the selected user. This creates a new Chrome container.
2. **Go to Session**: Opens a VNC viewer to interact with the Chrome browser.
3. **End Session**: Stops and removes the Chrome container.
4. **Start Automation**: Begins running the basic automation script in the Chrome container. Simple custom data can be entered in the provided fields.
5. **Stop Automation**: Halts the running automation script.

## Custom Data

Users can input basic custom data through the web interface. This data is passed to the automation script when it starts. The `customData` dictionary in `session_manager.py` can be customized for specific automation needs.

## Setup and Running

1. Ensure Docker and Docker Compose are installed on your system.
2. Clone this repository.
3. Navigate to the project directory.
4. Copy the `.env.example` file to `.env`:  
   ```
   cp .env.example .env
   ```
5. Edit the `.env` file and set the `HOST_IP` variable:
   - If running on a remote server, set it to the server's public IP address.
   - If running locally, set it to `localhost`.
6. Run `docker-compose up --build` to start the services.
7. Access the web interface at `http://localhost` or `http://<your-server-ip>`.


## Automation Script Documentation

The `AutomationScript` class in `automation_script.py` serves as a base class for all automation scripts. Here's a brief overview of its key components:

- `__init__(self, website_url, user_id)`: Initializes the script with the target website and user ID.
- `require_authentication(self)`: Abstract method to determine if the script requires user authentication.
- `is_logged_on(self)`: Abstract method to check if the user is currently logged in.
- `login(self)`: Abstract method to perform the login process.
- `automation_process(self)`: Abstract method containing the main automation logic.
- `setup_driver_with_profile(self)`: Sets up the Selenium WebDriver with the user's Chrome profile.
- `run(self, stop_event)`: Main method to run the automation script, handling setup, execution, and cleanup.

To create a custom automation script:

1. Create a new class that inherits from `AutomationScript`.
2. Implement the abstract methods according to your specific automation needs.
3. Override the `automation_process` method with your custom automation logic.
4. Use the `self.driver` attribute to interact with the browser.
5. Utilize the `self.custom_data` dictionary to access user-provided custom data.

Example (in `fieldnation_script.py`):

