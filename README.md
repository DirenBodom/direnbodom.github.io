---
title: Bronn - Music recommendation bot
description: Describes how run the bot, current features, and code snippets to explain how it the features were implemented.
keywords: 
---

<style type="text/css">
  body {
    margin: auto;
	width: 50%;
	padding: 10px;
  }
  .language-Python3 {background: rgba(0, 128, 0, 0.3);}
</style>

# Bronn Music Recommendation Bot

The *Bronn Bot* was created to help users find music through a bot developed using the [Bot Framework](https://dev.botframework.com).
In this document we'll go through how to run Bronn on your local machine, as well has the key components which the bot is built upon.

`Demonstration of how Bronn reacts to a neutral user greeting.`

![Bronn intro demo](../images/bronn-demo.png)

## Prerequisites

### Install Python 3.6 - 3.8
Currently the bot will only work if you run it using Python versions 3.6 to 3.8

### Download the code
You can find the bot code at its [Github Repository](https://github.com/DirenBodom/Bronn-Bot/tree/master). Make sure that you are using the master branch.

### Running the sample
- Run `pip install -r requirements.txt` to install all dependencies
- Run `python app.py`

### Testing the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the Bot Framework Emulator version 4.3.0 or greater from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- Enter a Bot URL of `http://localhost:3978/api/messages`

## Key Components

The bot's main features currently are:
- Waterfall dialogs which maintain a continous conversation with the users
- Adaptive cards that provide key information for recommended songs, album art, and a link for the user to learn more about the recommendation
- Default data set of available recommendations, consisting of songs from multiple genres
- Interruption handling that give the user options to end the conversation
- Natural language processing through the Luis AI. This enables detection of user's feelings and genre detection.

### Dialogs

There are 2 dialogs which the user interacts with:
- MainDialog: Dialog that provides the initial greet and uses recognizer to determine how to launch the RecommendationDialog
- Recommendation: Dialog that computes songs based on user input and keeps the conversation going through repeating the recommendation step.

You can see how the MainDialog dialog is created:
`app.py lines 72-79`
```Python3

# Create the Bot
RECOGNIZER = MusicRecognizer(CONFIG)
RECOMMENDATION_DIALOG = RecommendationDialog(RECOGNIZER)
DIALOG = MainDialog(RECOGNIZER, RECOMMENDATION_DIALOG)
BOT = MyBot(RECOGNIZER, CONVERSATION_STATE, USER_STATE, DIALOG)
 
```

Within the initiation of the MainDialog class, you can see that this dialog consists the steps `self.intro_step` and `self.act_step`. The first step is what greets the user initially
and the act step is what uses the Luis AI to recognize the user's intent and launch the RecommendationDialog accordingly.

`dialogs/main_dialog.py lines 25-33`
```Python3

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(recommendation_dialog)
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.intro_step, self.act_step]
            )
        )

```

### Recommendation Dialog

The recommendation dialog relies on the Luis AI input and/or choice promps to determine which genre to use. If the user's initial response contains a genre or feeling which can be
translated into a genre (if the user says *relaxing* the bot translates this to *classical*). Otherwise, we secure a genre through choice prompts. This can be seen in the following snippet:

`dialogs/recommendation_dialog.py lines 70-93`
```Python3

    async def genre_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If the user has not provided any emotion in their initial greeting or a genre that they're looking for.
        :param step_context:
        :return DialogTurnResult
        """
        recommendation_details = step_context.options

        # Inquire the user about the genre they'd like to listen to
        if recommendation_details["genre"] == "":
            message_text = "What kind of music would you like me to recommend?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            genre_choices = [Choice("rock"), Choice("metal"), Choice("classical"), Choice("jazz"), Choice("pop"), Choice("electronic")]
            return await step_context.prompt(
                ChoicePrompt.__name__, PromptOptions(prompt=prompt_message,choices=genre_choices)
            )
        
        return await step_context.next(recommendation_details)

```

To keep the conversation flowing after an initial recommendation has been provided, the dialog contains a confirmation step. The `self.confirmation_step` prompts the user on whether they
enjoyed the recommendation. If the user says yes, a new recommendation is given from the current genre in-use. Otherwise, a new prompt is generated for the user to choose a different genre.
On both occasions, the dialogue is replaced with a new to step back into the `self.recommendation_step`, but with a different *step_context* to create the aforementioned behavior.

`dialogs/recommendation_dialog.py lines 145-181`
```Python3

    async def confirmation_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Once a recommendation has been given, take action based on the user's feedback
        :param step_context:
        :return DialogTurnResult:
        """
        print("Executing confirmation step")
        recommendation_details = step_context.options
        feedback = step_context.result

        # If the user liked the recommendation, recommend another song from the same genre
        if feedback:
            message_text = "Glad you enjoyed it!"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )

            await step_context.context.send_activity(
                prompt_message
            )

            return await step_context.replace_dialog(RecommendationDialog.__name__, step_context.options)
        else:
            message_text = "Sorry to hear that."
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )

            await step_context.context.send_activity(
                prompt_message
            )

            step_context.options["genre"] = ""
            return await step_context.replace_dialog(RecommendationDialog.__name__, step_context.options)
```

### Adaptive Cards

Adaptive cards enhance the user's experience by showing song information, album art, and providing a link to open the song in a browser. To achieve this feature, the skeleton of the card is formed from
the `cards/songCard.json` file. 

![Adaptive Card song display](../images/adaptive-card-song.png)

Once the `self.recommendation_step` has computed a song to recommend, it reads the *songCard.json* file and updates the default values based on the selected song. Since each song is created using
the `SongClass.py`, extracting song properties is as simple as writing `song.artist`.

`dialogs/recommendation_dialog.py lines 115-133`
```Python3
        # Update the context genre
        step_context.options["genre"] = genre

        # Randomly select a song from the given genre
        song = songs[genre][random.randrange(3)]
        message_text = "I recommend listening to: "
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )
        await step_context.context.send_activity(
            prompt_message
        )
		
```

### Interruptions

Currently the bot supports a termination interruption to end the conversation. To achieve this, every time the dialogue continues; the program checks for termination keywords.
Once the user triggers this interruption, all dialogues are immediately canceled. 