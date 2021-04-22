# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    RecognizerResult,
    UserState,
    MessageFactory,
    ConversationState,
)
from botbuilder.schema import ChannelAccount
from botbuilder.dialogs import Dialog
from dialogs.dialog_helper import DialogHelper
from config import DefaultConfig
from botbuilder.schema import InputHints

from music_recognizer import MusicRecognizer
from botbuilder.ai.luis import LuisRecognizer

class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.
    def __init__(
        self,
        luis_recognizer: MusicRecognizer,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog
    ):
        self._luis_recognizer = luis_recognizer

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog


    async def on_message_activity(self, turn_context: TurnContext):
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # Save any state changes that might have occurred during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)
    
    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                message_text = "Hello, I am the music recommending bot Bronn!"
                prompt_message = MessageFactory.text(
                    message_text, message_text, InputHints.expecting_input
                )
                await turn_context.send_activity(prompt_message)
                await DialogHelper.run_dialog(
                    self.dialog,
                    turn_context,
                    self.conversation_state.create_property("DialogState"),
                )
