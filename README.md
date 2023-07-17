# MICA - MedIa Control Application

## Components and capabilities

### Core

- _events_ - Manages handlers and events
    - add event handler
    - call event (executed in separate thread)
- _settings_ - Store application configuration(in .ini format)

### Modules

- _browser_ (chrome)
    - open link by url
    - open YouTube video by query
    - show gifs by query (interval taken from config)
- _listener_ - call events based on voice input
- _web_interface_ - control app from external browser
    - call events
    - change settings
- _updater_
    - update and restart app on git updates (can be disabled in config)
