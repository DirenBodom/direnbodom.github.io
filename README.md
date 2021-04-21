---
title: Bronn - Music recommendation bot
description: Describes how run the bot, current features, and code snippets to explain how it the features were implemented.
keywords: 
---

# Bronn Music Recommendation Bot

The *Bronn Bot* was created to help users find music through a bot developed using the [Bot Framework](https://dev.botframework.com).
In this document we'll go through how to run Bronn on your local machine, as well has the key components which the bot is built upon.

### Prerequisites

## Install Python 3.6 - 3.8
Currently the bot will only work if you run it using Python versions 3.6 to 3.8

## Download the code
You can find the bot code at its [Github Repository](https://github.com/DirenBodom/Bronn-Bot/tree/master). Make sure that you are using the master branch.

## Running the sample
- Run `pip install -r requirements.txt` to install all dependencies
- Run `python app.py`

## Testing the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the Bot Framework Emulator version 4.3.0 or greater from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- Enter a Bot URL of `http://localhost:3978/api/messages`

### Key Components

The bot's main features currently are:
-Waterfall dialogs which maintain a continous conversation with the users
-Adaptive cards that provide key information for recommended songs, album art, and a link for the user to learn more about the recommendation
-Default data set of available recommendations, consisting of songs from multiple genres
-Interruption handling that give the user options to end the conversation
-Natural language processing through the Luis AI. This enables detection of user's feelings and genre detection.

## Dialogs

There are 2 dialogs which the user interacts with:
-MainDialog: Dialog that provides the initial greet and uses recognizer to determine how to launch the RecommendationDialog
-Recommendation: Dialog that computes songs based on user input and keeps the conversation going through repeating the recommendation step.

You can see how the MainDialog dialog is created:
[!code-python[app](~/../app.py?range=72-79)]

