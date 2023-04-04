from flask import render_template,redirect, url_for,request
from app import app,db,api
from app.models import Warehouse,Product,Credential,Stok
from datetime import date
from flask_restful import Resource
from sqlalchemy import create_engine
import pandas as pd
import json

class apiv1(Resource):
    def post(self):
        if request.args.get('data')=="token":
            if request.args.get('secretkey')==app.config['SECRET_KEY']:
                cred=Credential.query.get(1)
                cred.clientBearer=request.args.get('newtoken')
                db.session.add(cred)
                db.session.commit()
                return {'status':'token updated'}
            else:
                return {'status':'wrong secret key'}
        else:
            id=request.args.get('id')
            qty=request.args.get('qty')
            wh=request.args.get('wh')
            print(id)
            print(qty)
            newdata=Stok(item_id=id,item_qty=qty,stok_date=date.today(),wh_id=wh)
            db.session.add(newdata)
            db.session.commit()
            return {'status':'added stok'}
    def get(self):
        if request.args.get('data')=="product":
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            df = pd.read_sql_query("SELECT * FROM product", con=engine)
            engine.dispose()
            df=df.to_json(orient='records')
            df=json.loads(df)
            return df
        elif (request.args.get('data')=="credentials"):
            if request.args.get('secretkey')==app.config['SECRET_KEY']:
                engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
                df = pd.read_sql_query("SELECT * FROM credential", con=engine)
                engine.dispose()
                df=df.to_json(orient='records')
                df=json.loads(df)
                return df
            else:
                return {'status':'wrong secret key'}
        else:
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            df = pd.read_sql_query("SELECT * FROM warehouse", con=engine)
            engine.dispose()
            df=df.to_json(orient='records')
            df=json.loads(df)
            return df
        
api.add_resource(apiv1,'/apiv1')


@app.route('/')
def index():
    return render_template('base.html')

@app.route('/stokhist')
def stokhist():
    df=Stok.query.all()
    return render_template('stokhist.html',df=df)

@app.route('/delstokhist/<id>')
def delstokhist(id):
    itemdel=Stok.query.get(id)
    db.session.delete(itemdel)
    db.session.commit()
    return redirect(url_for('stokhist'))

@app.route('/wh', methods=['GET', 'POST'])
def wh():
    df=Warehouse.query.all()
    if request.method=='POST':
        NewWh=Warehouse(warehouse_id=request.form['InpWhId'],warehouse_name=request.form['InpWhName'])
        db.session.add(NewWh)
        db.session.commit()
        return redirect(url_for('wh'))
    else:        
        return render_template('wh.html',df=df)
    
@app.route('/product', methods=['GET', 'POST'])
def prod():
    df=Product.query.all()
    if request.method=='POST':
        NewProd=Product(product_id=request.form['InpProdId'],product_status="Active")
        db.session.add(NewProd)
        db.session.commit()
        return redirect(url_for('prod'))
    else:        
        return render_template('product.html',df=df)
    
@app.route('/cred', methods=['GET', 'POST'])
def cred():
    df=Credential.query.get(1)
    if request.method=='POST':
        if request.form['action']=="Add Credential":
            NewCred=Credential(appId=request.form['InpAppId'],
                               clientId=request.form['InpClientId'],
                               clientSecret=request.form['InpClientSecret'],
                               clientBearer=request.form['InpClientBearer'])
            db.session.add(NewCred)
            db.session.commit()
            return redirect(url_for('cred'))
        else:
            df.appId=request.form['InpAppId']
            df.clientId=request.form['InpClientId']
            df.clientSecret=request.form['InpClientSecret']
            df.clientBearer=request.form['InpClientBearer']
            db.session.add(df)
            db.session.commit()
            # credential.query.all()
            return redirect(url_for('cred'))
    else:        
        return render_template('credential.html',df=df)