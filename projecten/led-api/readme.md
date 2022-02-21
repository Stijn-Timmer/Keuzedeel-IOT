### ledAPI 

Bestuur een simpele LED via een http API 

#### Arduino (CPP)

```CPP
#include <Arduino.h>

void setup() 
{
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Send an int 1 = ON 2 = off");

}

void loop()
{
  if (Serial.available())
  {
    int state = Serial.parseInt();
    if (state == 1)
    {
     digitalWrite(LED_BUILTIN, HIGH); 
     Serial.println("Command completed LED turned ON");
    }
    if (state == 2)
    {
     digitalWrite(LED_BUILTIN, LOW);
     Serial.println("Command completed LED turned OFF");
    }  
  }
}
```
In detail:

Start de serial connectie <code>while (!Serial);</code> wacht tot Python of een andere serial client een connectie maakt voordat de <code>void loop()</code> aangeroepen wordt.
```cpp
void setup() 
{
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  while (!Serial);

}
```

Vraag de integer op die door serial gestuurd als de int nog NULL is gebeurt er niks met de LED.

```cpp
  if (Serial.available())
  {
    int state = Serial.parseInt();
    if (state == 1)
    {
     digitalWrite(LED_BUILTIN, HIGH); 
     Serial.println("Command completed LED turned ON");
    }
    if (state == 2)
    {
     digitalWrite(LED_BUILTIN, LOW);
     Serial.println("Command completed LED turned OFF");
    }  
  }
```

### API (Python)

```python
from fastapi.responses import JSONResponse
from fastapi import FastAPI
import uvicorn
import serial
import time

api = FastAPI()

arduino = serial.Serial('COM5', 9600)

state = 0

with arduino: 
  arduino.setDTR(False)
  time.sleep(1)
  arduino.flushInput()
  arduino.setDTR(True)

@api.on_event("startup")
async def check_arduino():
    #Quickly connect to the arduino to check if it is working else throw exception
    arduino.open
    print(f'Connected to arduino on port: {arduino.name}')
    arduino.close


@api.get('/led/state')
async def get_state():
    if state == 1:
        return JSONResponse({'state': 'The LED is currently ON!'})
    return JSONResponse({'state': 'The LED is currently OFF!'})

@api.get('/led/on')
async def led_on():
    global state 
    state = 1
    with arduino: 
        time.sleep(1.5)
        arduino.write(b'1')
        time.sleep(0.5)
        serPort = arduino.name
        serMessage = (arduino.read(arduino.inWaiting()))
        arduino.close()

    #Format to respond with back to the browser or postman.
    respFormat = {
        'state': 'changed to OFF!',
        'debug': [
            {'serialMessage': f'{str(serMessage.decode("utf-8")).strip()}'},
            {'serialPort': f'{serPort}'}
        ]
    }
    return JSONResponse(respFormat)
    

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


if __name__ == "__main__":
    uvicorn.run("api:api", host="127.0.0.1", port=5000, log_level="info", debug=True)
```

Import pip libs
```python
from fastapi.responses import JSONResponse
from fastapi import FastAPI
import uvicorn
import serial
import time
```
Defineer de API en Arduino als python objects.

```python
api = FastAPI()
arduino = serial.Serial('COM5', 9600)
```
Gebruik het FastAPI startup event om een connectie uit te proberen bij de Arduino, zo niet? Exceptie en de api sluit zichzelf af.

```python
@api.on_event("startup")
async def check_arduino():
    arduino.open
    print(f'Connected to arduino on port: {arduino.name}')
    arduino.close
```

Vraag de huidige state van de LED op.

```python
@api.get('/led/state')
async def get_state():
    if state == 1:
        return JSONResponse({'state': 'The LED is currently ON!'})
    return JSONResponse({'state': 'The LED is currently OFF!'})
```

Response: 200 OK

```JSON
{"state": "The led is currently OFF!"}
```

Het uit en aanzetten van de LED

```python
@api.get('/led/on')
async def led_on():
    global state 
    state = 1
    with arduino: 
        time.sleep(1.5)
        arduino.write(b'1')
        time.sleep(0.5)
        serPort = arduino.name
        serMessage = (arduino.read(arduino.inWaiting()))
        arduino.close()

    #Format to respond with back to the browser or postman.
    respFormat = {
        'state': 'changed to OFF!',
        'debug': [
            {'serialMessage': f'{str(serMessage.decode("utf-8")).strip()}'},
            {'serialPort': f'{serPort}'}
        ]
    }
    return JSONResponse(respFormat)
    

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
```

Response: 200 OK

```JSON
{
   "state":"changed to OFF!",
   "debug":[
      {
         "serialMessage":"Command completed LED turned OFF"
      },
      {
         "serialPort":"COM5"
      }
   ]
}
```

Start de ASGI app met uvicorn 

```python
if __name__ == "__main__":
    uvicorn.run("api:api", host="127.0.0.1", port=5000, log_level="info", debug=True)
```
