# Water Sensor Telegram Bot

This is the impementation of the water sensor connected to Raspberry PI and the Telegram Bot for it. Telegram Bot will notify any subscribers about exceeding the water limit.

## Dependencies

To install dependencies and insure the smooth running create a virtual Python environment and install dependencies from there.

```bash
# create venv
python3 -m venv ./.venv

# activate venv
source ./.venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

## Configuration

Make a copy of example environment and insert the Telegram Bot API key

## Water sensor

To get the sensor data and record it in the file use the following command. To make things simplier you do not need to enable virtual environment for the sensor script. Add it to the crontab if needed.

```bash
python3 sensor.py > level.txt 2 >& 1
```

## Telegram Bot

To launch the bot enter the below command (remember to activate virtual environemnt first). Bot can then later be added as a service.

```bash
python main.py
```

To handle notifications bot is going to manage an additional ```subscribers.txt``` text file with the list of chats. When bots is restarted, it will check for that file and create notification tasks accordingly. 
