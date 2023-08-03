# Plane over me 
### Description
Telegram bot for live skywatching. Instantly detects up to 5 planes closest to you and provides their altitude, speed, direction, distance from your position. 
- Draws a map of aircraft positions using [Static Google Maps](https://developers.google.com/maps/documentation/maps-static)
- Retrieves photos of aircraft by their registration numbers using site parsing [www.jetphotos.com](https://www.jetphotos.com/)   
- Retrieves current aviation data using the [ADS-B Exchange API](https://rapidapi.com/adsbx/api/adsbx-flight-sim-traffic).
### Technologies
`pyTelegramBotAPI`
`beautifulsoup`
`pandas`

### How to launch the project 
- Clone the repository
```
git clone git@github.com:antoncp/plane_over_me_bot.git
``` 
- Create and activate virtual environment
```
python3.9 -m venv venv
``` 
- Install dependencies from requirements.txt file with activated virtual environment
```
pip install -r requirements.txt
```
- Execute a command to run the bot in a polling mode 
```
python main.py
```

### Preconfigured GitHub Actions workflow
After forking the repository, use the workflow [Deploy to Digital Ocean](https://github.com/antoncp/plane_over_me_bot/blob/main/.github/workflows/digital_deploy.yml) from the `.github` folder for quickly assess code quality with `flake8` and fast deploy to the production server.   