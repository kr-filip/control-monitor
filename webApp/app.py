from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import time
import serial

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

def background_thread(args):
    count = 0  
    dataCounter = 0
    dataList = []
    controlValueList=[]
    timestampList=[]
    timestamp=0
    controlValue=0
    db_value = ""
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    cursor = db.cursor()
    cursor.execute("SELECT MAX(id) FROM projekt")
    maxid = cursor.fetchone()
    db.close()
    idNumber=maxid
    ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate =9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
     )
    while True:
        if args:
          A = dict(args).get('A')
          controlValue=dict(args).get('controlValue')
          db_value=dict(args).get('db_value')
        else:
          controlValue=0
          A = 0
          db_value = ''
          idNumber=str(maxid) 
        #print(A)
        #print(dbV) 
        #print(args)  
        socketio.sleep(2)
        count += 1
        dataCounter +=1
        timeStamp=time.asctime(time.localtime(time.time()))
        ser.flushInput()
        serialData=ser.read(3)
        if (len(serialData)!=0):
            ser.flushInput()
            serialData=float(ser.read(3))
        else:
            serialData=0
#  
        if (type(controlValue)==type('str')):
#             
            if ((float(controlValue) >= 0) & (float(controlValue) <= 3.3)):
                ser.flushOutput()
                ser.write(bytes(controlValue,'utf-8'))
                        
            print(bytes(controlValue,'utf-8'))
            print(type(controlValue) == type('str'))

        if db_value == 'start':
            dataDict = {
            "time": timeStamp,
            "controlValue": controlValue,
            }         
            dataList.append(dataDict)

        else:
          if len(dataList)>0:
            dataString = str(dataList).replace("'", "\"")
            dataString=str(dataString)         
            cursor = db.cursor()
            cursor.execute("SELECT MAX(id) FROM projekt")
            maxid = cursor.fetchone()
            cursor.execute("INSERT INTO projekt (id, data) VALUES (%s, %s)", (maxid[0] + 1, dataString))
            db.commit()
            dataList = []
            controlValueList=[]
            timestampList=[]
            dataCounter = 0
            db.close()
            
        socketio.emit('my_response',
                      {'data': serialData, 'count': count, 'timeStamp': timeStamp, 'maxId':maxid},
                      namespace='/test')  
         

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)
   
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['data']
    session['controlValue']=0

@socketio.on('my_event2', namespace='/test')
def test_message2(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['controlValue'] = message['controlValue'] 

@app.route('/database', methods=['GET', 'POST'])
def graph():
    return render_template('database.html', async_mode=socketio.async_mode)

@socketio.on('db_read', namespace='/test')
def db_message(message):   
    session['idNumber']=message["idNumber"]
    print(session['idNumber'])
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    cursor = db.cursor()
    cursor.execute("SELECT  data FROM  projekt WHERE id=%s",session.get('idNumber'))
    rv = cursor.fetchall()
    db.close()
    
    socketio.emit('my_response2',
                  {'data': rv, 'count': session.get('count', 0), 'timeStamp': 1, 'maxId': session.get('maxid')},
                  namespace='/test')
   
@socketio.on('db_event', namespace='/test')
def db_message2(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['db_value'] = message['value']
    print(session['db_value'])

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},namespace='/test')
    disconnect()
    session['A']="Client disconnected"

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected to server', 'count': 0},namespace='/test')


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
