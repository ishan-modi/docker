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
        obj = name_score.name_scoring()
        obj.forming(file_data)
        obj.clean()
        obj.scoring()
        data={
            'name':obj.get_name()
        }
        resp=jsonify(data)
        return resp
    
api.add_resource(extract_name,"/")