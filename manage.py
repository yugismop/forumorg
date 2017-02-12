from flask_script import Manager
from forum import app
from flask_assets import ManageAssets

manager = Manager(app)
manager.add_command("assets", ManageAssets())

if __name__ == "__main__":
    manager.run()
