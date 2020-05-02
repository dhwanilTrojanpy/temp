from flask import Flask

from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging
import os


app = Flask(__name__)
CORS(app)
api = Api(app)
logging.basicConfig(filename="donutdash.log", 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    filemode='w')


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__)) + '/uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
db = SQLAlchemy(app)

logger=logging.getLogger()
logger.setLevel(logging.DEBUG) 
import models,resources


# @app.before_first_request
# def create_tables():
    # db.create_all()
#     db.session.commit()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)



api.add_resource(resources.IP, '/pi/ip',resource_class_kwargs={
    'logger': logger
})
# api.add_resource(resources.UserRegistration, '/pi/registration')
api.add_resource(resources.UserLogin, '/pi/login',resource_class_kwargs={
    'logger': logger
})
# api.add_resource(resources.UserLogoutAccess, '/pi/logout/access')
# api.add_resource(resources.UserLogoutRefresh, '/pi/logout/refresh')
api.add_resource(resources.TokenRefresh, '/pi/token/refresh',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Allusers, '/pi/users',resource_class_kwargs={
    'logger': logger
})
# api.add_resource(resources.SecretResource, '/pi/secret')
api.add_resource(resources.Taskmanagement, '/pi/taskmanager',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.ProcessAction, '/pi/process_action',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.ServiceManagement, '/pi/service',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.ServiceAction, '/pi/service_action',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.ServiceDetails, '/pi/service_detail',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.PortManagement, '/pi/port',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.PortKill, '/pi/port_action',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Networkinfo, '/pi/networkinfo',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Memoryinfo, '/pi/memoryinfo',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Traffic, '/pi/traffic',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Wificontroller, '/pi/wificontrole',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Getfilefolder,'/pi/filefolder',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Displaypartition, '/pi/partition',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Createpartition, '/pi/create_partition',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.partNumber, '/pi/create_partition/partnumber',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.First, '/pi/create_partition/first',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Last, '/pi/create_partition/last',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.UserOperation, '/pi/userOperation',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Wifilist,'/pi/wifilist',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Ramusage,'/pi/ramusage',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Revision,'/pi/revision',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Downlaodfile,'/pi/downloadfile',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Cputemp,'/pi/monitor',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Uploadfile,'/pi/fileupload',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Createfile,'/pi/createfile',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Delfile,'/pi/delfile',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Copyfile,'/pi/copyfile',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Createdir,'/pi/createdir',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Deldir,'/pi/deldir',resource_class_kwargs={
    'logger': logger
})
api.add_resource(resources.Copydir,'/pi/copydir',resource_class_kwargs={
        'logger': logger
        })
api.add_resource(resources.Movefiledirs,'/pi/movefiledir',resource_class_kwargs={
    'logger': logger
})

api.add_resource(resources.CheckExist,'/pi/checkexist',resource_class_kwargs={
    'logger' : logger
})

api.add_resource(resources.Readfile,'/pi/readfile',resource_class_kwargs={
    'logger' : logger
})

api.add_resource(resources.WriteFile,'/pi/writefile',resource_class_kwargs={
    'logger' : logger
})




    
if __name__ == '__main__':
    app.run()
    
