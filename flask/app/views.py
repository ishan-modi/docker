import os
import json
from pdf2words import name_score
from flask import Flask,jsonify
from flask_restful import Api,Resource,request
from app import app

api=Api(app)

class extract_name(Resource):
    def get(self):
        return "flask app running"

    def post(self):
        file_data = request.files['file'].read()
        file_data=json.loads(file_data)
        obj1 = name_score.name_scoring()
        obj1.forming(file_data)
        obj1.clean()
        obj1.scoring()
        
        obj2 = addr_score.addr_scoring()
        obj2.forming(file_data)
        obj2.clean()
        obj2.scoring()

        data={
            'name':obj1.get_name(),
            'address':obj2.get_addr()
        }
        resp=jsonify(data)
        return resp
    
api.add_resource(extract_name,"/")