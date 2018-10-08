from flask import Flask, jsonify, request, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, create_engine, LargeBinary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from io import BytesIO

app = Flask(__name__)
Base = declarative_base()


class Quarter(Base):
    __tablename__ = 'quarter'
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(String(50), nullable=False)


class Items(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    item_name = Column(String)
    quantity = Column(String)
    price = Column(Integer)
    quarter_id = Column(Integer, ForeignKey("quarter.id"))
    quarter = relationship(Quarter)


class Before_Imgs(Base):
    __tablename__ = 'before_images'
    id = Column(Integer, primary_key=True)
    room_image = Column(LargeBinary)
    quarter_id = Column(Integer, ForeignKey("quarter.id"))
    quarter = relationship(Quarter)

class After_Imgs(Base):
    __tablename__ = 'after_images'
    id = Column(Integer, primary_key=True)
    room_image = Column(LargeBinary)
    quarter_id = Column(Integer, ForeignKey("quarter.id"))
    quarter = relationship(Quarter)



engine = create_engine('sqlite:///quarter.db')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


@app.route('/quarters', methods=['GET'])
def getAllEmp():
    dic = []
    session = Session()
    users = session.query(Quarter).all()
    for u in users:
        dic.append({"owner": u.owner, "id": u.id})
    return jsonify(dic), 200


@app.route('/quarter/<getId>', methods=['GET'])
def getEmp(getId):
    dic = {}
    session = Session()
    quarter = session.query(Quarter).filter(Quarter.id == getId).one()

    items = session.query(Items).filter(Items.quarter_id == quarter.id).all()
    data = []
    for d in items:
        data.append({"item_name":d.item_name, "quantity": d.quantity, "price": d.price, "Items ID": d.id})
    print(items)

    dic.update({"owner": quarter.owner, "id": quarter.id, "items": data})
    return jsonify(dic), 200


@app.route('/update/quarter/<Id>', methods=['PUT'])
def updateEmp(Id):
    session = Session()
    user = session.query(Quarter).filter(Quarter.id == Id).one()
    user.owner = request.json['owner']

    session.add(user)
    session.commit()
    dic = {"id": user.id, "owner": user.owner}
    return jsonify(dic) , 201


@app.route('/create_quarter', methods=['POST'])
def createEmp():
    session =Session()
    quarter = Quarter()
    quarter.owner = request.json['owner']
    session.add(quarter)
    session.commit()
    dic = {"id": quarter.id, "owner": quarter.owner}
    return jsonify(dic), 201


@app.route('/upload/img/<Id>', methods=['POST'])
def ubeforeImg(Id):
    session = Session()
    file = request.files["roomImage"]
    newfile = Before_Imgs(room_image=file.read())
    newfile.quarter_id = Id
    session.add(newfile)
    session.commit()
    return "Done", 201


@app.route('/download/img/<Id>', methods=['GET'])
def dbeforeImg(Id):
    session = Session()
    file_data = session.query(Before_Imgs).filter(Before_Imgs.quarter_id == Id).one()
    return send_file(BytesIO(file_data.room_image), attachment_filename='h.png', as_attachment=True), 201


@app.route('/add_items/<Id>', methods=['POST'])
def createDesc(Id):
    session = Session()
    items = Items()
    items.quarter_id = Id
    items.item_name = request.json['item_name']
    items.quantity = request.json['quantity']
    items.price = request.json['price']

    session.add(items)
    session.commit()
    dic = {"item_name": items.item_name,
           "quantity": items.quantity, "price": items.price}
    return jsonify(dic),201


@app.route('/delete/quarter/<Id>', methods=['DELETE'])
def deleteEmp(Id):
    session = Session()
    u = session.query(Quarter).filter(Quarter.id == Id).one()
    session.delete(u)
    session.commit()
    return " Record Deleted", 200


@app.route('/delete/item/<Id>', methods=['DELETE'])
def deleteitem(Id):
    session = Session()
    u = session.query(Items).filter(Items.id == Id).one()
    session.delete(u)
    session.commit()
    return " Items Deleted", 200



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
