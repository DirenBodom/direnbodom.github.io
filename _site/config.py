#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    LUIS_APP_ID = os.environ.get("LuisAppId", "a0305c1b-3d59-4187-a480-169448360ba5")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "52692519474a4e359e5f5d124b3cf2ce")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westus.api.cognitive.microsoft.com")
    # ID: 6ed34be8-ecde-4269-9f9c-4b593f1d7d82
    # Password: 015ddbfb-efba-46e8-8a69-ebe4b5195675, yC8tbupjqJ2DPSwKyVI-CDraB..810-1--
