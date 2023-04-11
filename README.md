# MICA - MedIa Control Application

## Structure

### Application

- Core: Control events and modules
- Modules: Create and listen to events

### Core

- Eventer: Manages handlers and events (Observer)  
  Allows:
    - Subscribing to events
    - Adding events
- Updater: Controls app auto-update

### Modules

- Web UI: Configure and manually control events
- Speech to Text: Creates events based on keywords (Vosk + Scikit-Learn)
- Text to Speech: Comments on the current event
- WebDriver: For working with the browser (Selenium)

## TODO:
- Speech to Text
- Animated overlay