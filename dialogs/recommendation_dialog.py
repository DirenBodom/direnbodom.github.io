from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult, ComponentDialog
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions, ConfirmPrompt, ChoicePrompt
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from botbuilder.ai.luis import LuisRecognizer
from music_recognizer import MusicRecognizer
from botbuilder.schema import Attachment
from botbuilder.dialogs.choices import Choice
import random
import json
import os.path

class RecommendationDialog(CancelAndHelpDialog):
    def __init__(self, recognizer: MusicRecognizer, dialog_id: str = None):
        super(RecommendationDialog, self).__init__(dialog_id or RecommendationDialog.__name__)
        self.luis_recognizer = recognizer
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.genre_step,
                    self.recommend_step,
                    self.confirmation_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__
    
    def create_adaptive_card_attachment(self, art: str, title: str, alb: str, img_url: str = None):
        relative_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(relative_path, "../cards/songCard.json")
        with open(path) as in_file:
            card = json.load(in_file)
        # Song properties
        artist = art
        song = title
        album = alb

        # Assign song values to the card
        column0 = card['body'][0]['columns'][0]['items']
        column0[0]['text'] = 'Artist: ' + artist
        column0[1]['text'] = 'Song: ' + song
        column0[2]['text'] = 'Album: ' + album

        # Update the Google search link url
        artist_arr = artist.split(" ")
        song_arr = song.split(" ")
        base_url = "https://www.google.com/search?q="

        for token in artist_arr:
            base_url += token + "+"
        for token in song_arr:
            base_url += token + "+"

        column0[3]['items'][0]['actions'][0]['url'] = base_url.lower()

        # Update the image location if you have an image url
        if not img_url is None:
            column1 = card['body'][0]['columns'][1]['items']
            column1[0]['url'] = img_url

        
        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive", content=card
        )

    async def genre_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If the user has not provided any emotion in their initial greeting or a genre that they're looking for.
        :param step_context:
        :return DialogTurnResult
        """

        print("Started a recommendation dialog!")

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
    
    async def recommend_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        recommendation_details = step_context.options
        songs = recommendation_details["songs"]
        genre = ''
        if (recommendation_details["genre"] == ""):
            result = step_context.result.value
            genre = result
        else:
            luis_result = await self.luis_recognizer.recognize(step_context.context)
            entities = luis_result.entities
            genre = recommendation_details["genre"]

        # Convert emotial states to genre equivalents
        if genre == "upbeat":
            genre = "pop"
        elif genre == "calm":
            genre = "jazz"
        elif genre == "relaxing":
            genre = "classical"
        elif genre == "heavy metal":
            genre = "metal"

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

        # Show card for this song
        song_card = self.create_adaptive_card_attachment(song.artist, song.song, song.album, song.image_url)
        response = MessageFactory.attachment(song_card)
        await step_context.context.send_activity(response)

            
        # Ask the user for a review
        message_text = "Did you enjoy my recommendation?"
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

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
            # Load attachment from file.
    



