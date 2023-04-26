# OnlyGame
# To use this game you will need to:
1. First of all, install python 3 versions on the official website:
https://www.python.org/downloads/
2. Cloning repository on your PC:
```
git clone https://github.com/IgorBukharevich/OnlyGame.git
```
---
3. Create a '.env' file and configure the game settings in the root of the project:
* Add these parameters to the file
```
# SETTINGS SERVER
# In field HOST = "IP_SERVER" in Field PORT = integer number - PORT_SERVER
HOST = ""
PORT = 

# SIZE MAP - SERVER
# Default recommended parameters (WIDTH_MAP = 4000, HEIGHT_MAP = 4000)
WIDTH_MAP = 4000
HEIGHT_MAP = 4000

# VISIBLE ALL OBJECTS FOR MAP - SERVER
# Default recommended parameters (small_WIDTH = 300, small_HEIGHT = 300)
small_WIDTH = 300
small_HEIGHT = 300

# SETTINGS WINDOW
# Default recommended parameters (WIN_WIDTH = 1000, WIN_HEIGHT = 800)
WIN_WIDTH = 1920
WIN_HEIGHT = 1080

# NAME_PLAYER
# In field PLAYER_NAME = "your nickname"
PLAYER_NAME = "KY-KY"
```
4. Install all dependencies, enter the command in the terminal:
```
python -m pip install -r requirements.txt
```
5. The "run" is launched first server.py " -> then "run_client.py "
provided that you are at the root of the project:
```
python run_server.py
python run_client.py 
```
# All of you are in the game! Good luck! =)