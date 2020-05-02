# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # See important note below
# import models

# db.create_all()
# db.session.commit()


# if __name__ =="__main__":
#     app.run()
from picontroller.RpiFilemanager import Filemanager

obj=Filemanager()
obj.editFile("/home/dhwanil/Desktop/file.py")
