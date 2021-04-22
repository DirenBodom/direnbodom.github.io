from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, TurnContext
from music_recognizer import MusicRecognizer
from botbuilder.core import MessageFactory, TurnContext
from botbuilder.schema import InputHints
from dialogs.recommendation_dialog import RecommendationDialog
from Song import SongClass

from botbuilder.ai.luis import LuisRecognizer

class MainDialog(ComponentDialog):
    def __init__(
        self, recognizer: MusicRecognizer, recommendation_dialog: RecommendationDialog
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self.recognizer = recognizer
        self.recommendation_dialog_id = recommendation_dialog.id

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(recommendation_dialog)
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.intro_step, self.act_step]
            )
        )

        self.songs = {'rock': [],
                        'metal': [],
                        'classical': [],
                        'jazz': [],
                        'pop': [],
                        'electronic': []}

        self.rock = [
                     ['Tame Impala', 'Lucidity', 'Innerspeaker', 'https://upload.wikimedia.org/wikipedia/en/d/dc/Tame_Impala_-_Innerspeaker.png'], 
                     ['King Gizzard and the Lizard Wizard', 'Rattlesnake', 'Flying Microtonal Banana', 'https://img.discogs.com/Dsx2WfNSZ0G3SWPY9wduXsKblqs=/fit-in/300x300/filters:strip_icc():format(jpeg):mode_rgb():quality(40)/discogs-images/R-9885063-1488706851-7952.jpeg.jpg'],
                     ['Temples', 'Sun Structures', 'Sun Structures', 'https://upload.wikimedia.org/wikipedia/en/5/58/Temples_-_Sun_Structures.png']
                    ]
        self.metal = [
                      ['Megadeth', 'Lucretia', 'Rust in Peace', 'https://upload.wikimedia.org/wikipedia/en/d/dc/Megadeth-RustInPeace.jpg'],
                      ['Annihilator', 'Alison Hell', 'Alice in Hell', 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3a/AnnihilatorAliceInHell.jpg/220px-AnnihilatorAliceInHell.jpg'],
                      ['Metallica', 'One', '...And Justice for All', 'https://upload.wikimedia.org/wikipedia/en/b/bd/Metallica_-_...And_Justice_for_All_cover.jpg']
                     ]
        self.classical = [
                          ['Chopin', 'Etude Op.10 No.3 in E Major', '', 'https://m.media-amazon.com/images/I/71DCffFhbYL._SS500_.jpg'],
                          ['Antonio Vivaldi', 'Four Seasons', '', 'https://www.baroquemusic.org/19Large.jpg'],
                          ['Camille Saint-Saëns', 'Danse Macabre', '', 'https://images-na.ssl-images-amazon.com/images/I/71C2-Lw5wUL._SX355_.jpg']
                         ]
        self.jazz = [
                        ['McCoy Tyner', 'When Sunny Gets Blue', 'Today and Tomorrow', 'https://upload.wikimedia.org/wikipedia/en/e/ec/Today_and_Tomorrow.jpg'],
                        ['Beegie Adair', 'What A Difference A Day Makes', 'A Time For Love: Jazz Piano Romance', 'https://images-na.ssl-images-amazon.com/images/I/711WxGESziL._SX355_.jpg'],
                        ['Jack Jezzro', 'Wave', 'Cocktail Party Bossa Nova', 'https://images-na.ssl-images-amazon.com/images/I/81GP9iBusPL._SY355_.jpg']
                    ]
        self.pop = [
                    ['Michelle Branch', 'Game of Love', 'Shaman', 'https://upload.wikimedia.org/wikipedia/en/b/b2/Santana_-_Shaman_-_CD_album_cover.jpg'],
                    ['Khriz y Angel', 'Ven Bailalo', 'Ven Bailalo (Reggaeton Mix)', 'https://m.media-amazon.com/images/I/61YsVHHg-NL._SS500_.jpg'],
                    ['Foster the People', 'Helena Beat', 'Torches', 'https://upload.wikimedia.org/wikipedia/en/d/d3/Torches_foster_the_people.jpg']
                   ]
        self.electronic = [
                            ['Linea Aspera', 'Synapse', 'Linea Aspera', 'https://img.discogs.com/XDDumr9vpZBh1lcBmxx6BB8yetM=/fit-in/600x600/filters:strip_icc():format(jpeg):mode_rgb():quality(90)/discogs-images/R-3831443-1346116401-7418.jpeg.jpg'],
                            ['New Order', 'Blue Monday', 'Substance', 'https://images-na.ssl-images-amazon.com/images/I/31RRJ84EK6L.jpg'],
                            ['Kraftwerk', 'Numbers', 'Computer World', 'https://upload.wikimedia.org/wikipedia/en/a/a6/Kraftwerk_-_Computer_World.png']
                          ]

        # Create objects from the above lists and add them to the songs list
        for song in self.rock:
            song_obj = SongClass(song[0], song[1], song[2], song[3])
            self.songs['rock'].append(song_obj)

        for song in self.metal:
            song_obj = SongClass(song[0], song[1], song[2], song[3])
            self.songs['metal'].append(song_obj)
        
        for song in self.classical:
            song_obj = SongClass(song[0], song[1], song[2], song[3])
            self.songs['classical'].append(song_obj)
        
        for song in self.jazz:
            song_obj = SongClass(song[0], song[1], song[2], song[3])
            self.songs['jazz'].append(song_obj)
        
        for song in self.pop:
            song_obj = SongClass(song[0], song[1], song[2], song[3])
            self.songs['pop'].append(song_obj)
        
        for song in self.electronic:
            song_obj = SongClass(song[0], song[1], song[2], song[3])
            self.songs['electronic'].append(song_obj)

        self.initial_dialog_id = "WFDialog"
    
    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self.recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)
        
        message_text = (
            str(step_context.options)
            if step_context.options
            else "How are you doing today?"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )
    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self.recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )
        
        # Get the intent and the sentiment
        luis_result = await self.recognizer.recognize(step_context.context)
        intent = LuisRecognizer.top_intent(luis_result)
        entities = luis_result.entities
        sentiment = luis_result.properties["sentiment"]["label"]
        message = ""
        options = {"genre": "", "confirmation": "", "sentiment": "", "songs": self.songs}


        print(intent)

        # If the user greeted back
        if intent == "Greetings":
            print("Got a greeting")
            if sentiment == "neutral":
                return await step_context.begin_dialog(self.recommendation_dialog_id, options)
            elif sentiment == "positive":
                message_text = "That's great to hear!"
                prompt_message = MessageFactory.text(
                    message_text, message_text, InputHints.expecting_input
                )
                await step_context.context.send_activity(prompt_message)

                options["genre"] = "pop"
                return await step_context.begin_dialog(self.recommendation_dialog_id, options)
            elif sentiment == "negative":
                message_text = "Sorry to hear that."
                prompt_message = MessageFactory.text(
                    message_text, message_text, InputHints.expecting_input
                )
                # Send the user a consent message
                await step_context.context.send_activity(prompt_message)

                # Set the genre to classical and begin recommendation dialogue
                options["genre"] = "classical"
                return await step_context.begin_dialog(self.recommendation_dialog_id, options)
        elif intent == "Recommendation":
            if "genre" in entities:
                options["genre"] = entities["genre"][0]
            return await step_context.begin_dialog(self.recommendation_dialog_id, options)
        else:
            didnt_understand_text = (
                "Sorry, I understand you. Please ask me about what kind of music you're looking for"
            )
            didnt_understand_message = MessageFactory.text(
                didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(didnt_understand_message)
            
        return await step_context.next(None)

        

