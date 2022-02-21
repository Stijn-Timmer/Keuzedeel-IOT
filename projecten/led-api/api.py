from fastapi.responses import JSONResponse
from fastapi import FastAPI
import uvicorn
import serial
import time

#define api object
api = FastAPI()

#define arduino serial object
arduino = serial.Serial('COM5', 9600)

# Define led startup state 
# 0 = off
# 1 = on

state = 0

# RESET ARDUINO

with arduino: 
  arduino.setDTR(False)
  time.sleep(1)
  arduino.flushInput()
  arduino.setDTR(True)

#Startup EVENT

@api.on_event("startup")
async def check_arduino():
    #Quickly connect to the arduino to check if it is working else throw exception
    arduino.open
    print(f'Connected to arduino on port: {arduino.name}')
    arduino.close


#API STATES

@api.get('/led/state')
async def get_state():
    if state == 1:
        # if state is 1 you can always return ON since the global variable and arduino resets on reloading of this API.
        return JSONResponse({'state': 'The LED is currently ON!'})
    return JSONResponse({'state': 'The LED is currently OFF!'})

@api.get('/led/on')
async def led_on():
    global state 
    state = 1
    with arduino: 
        #Wait here for some seconds for the arduino to reset
        time.sleep(1.5)
        #Write the byte trough serial to activate the LED
        arduino.write(b'1')
        #Wait for a response
        time.sleep(0.5)
        serPort = arduino.name
        serMessage = (arduino.read(arduino.inWaiting()))
        arduino.close()

    #Format to respond with back to the browser or postman.
    respFormat = {
        'state': 'changed to OFF!',
        'debug': [
            #Some extra decoding here since the response from serial are bytes
            #convert to UTF 8 and strip it from newlines such as \\n \\m
            {'serialMessage': f'{str(serMessage.decode("utf-8")).strip()}'},
            {'serialPort': f'{serPort}'}
        ]
    }
    #Return the response here
    return JSONResponse(respFormat)


#Do the same here as above but reverse some things to match the off state

@api.get('/led/off')
async def led_off():
    global state 
    state = 0
    with arduino: 
        time.sleep(1.5)
        arduino.write(b'2')
        time.sleep(1.5)
        serPort = arduino.name
        serMessage = (arduino.read(arduino.inWaiting()))
        arduino.close()

    respFormat = {
        'state': 'changed to OFF!',
        'debug': [
            {'serialMessage': f'{str(serMessage.decode("utf-8")).strip()}'},
            {'serialPort': f'{serPort}'}
        ]
    }

    return JSONResponse(respFormat)


# Tell uvicorn to host this ASGI application.
if __name__ == "__main__":
    uvicorn.run("api:api", host="127.0.0.1", port=5000, log_level="info", debug=True)
