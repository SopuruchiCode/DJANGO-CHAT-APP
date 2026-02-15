from channels.generic.websocket import AsyncWebsocketConsumer
from json import loads, dumps
from asgiref.sync import sync_to_async
from .models import Messages, Conversation
from django.contrib.auth import get_user_model
from accounts.models import Account
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


USER_MODEL = get_user_model()


def get_convo(usrname, friend_usrname):
    try:
        user_acc = Account.objects.get(user__username=usrname)
        friend_acc = Account.objects.get(user__username=friend_usrname)
    except ObjectDoesNotExist:
        return None

    else:
        conversations = Conversation.objects.all().filter(
            Q(participant_1=user_acc) | Q(participant_2=user_acc)).filter(
            Q(participant_1=friend_acc) | Q(participant_2=friend_acc))

        if conversations.count() == 1:
            conversation = conversations.first()
            return conversation.id


def get_account(search_query):
    user_acc = Account.objects.filter(user__username__startswith=search_query)
    acc_list = []
    for i in user_acc:
        data = {
            "username": f"@{i.user.username}",
            "profile_pic_path": f"{i.profile_picture.url}"
        }
        acc_list.append(data)
    return acc_list


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
        username = self.scope["user"].username
        # friend_username = self.scope["url_route"]["kwargs"].get("friend_username")
        # print(username, "connected via websocket")
        #
        # def get_convo(usrname, friend_usrname):
        #     user_acc = Account.objects.get(user__username=usrname)
        #     friend_acc = Account.objects.get(user__username=friend_usrname)
        #
        #     conversations = Conversation.objects.all().filter(
        #         Q(participant_1=user_acc) | Q(participant_2=user_acc)).filter(
        #         Q(participant_1=friend_acc) | Q(participant_2=friend_acc))
        #
        #     if conversations.count() == 1:
        #         conversation = conversations.first()
        #         return conversation.id
        #
        # convo_id = await sync_to_async(get_convo)(username, friend_username)
        # self.convo_id = str(convo_id)
        # await self.channel_layer.group_add(self.convo_id, self.channel_name)

        await self.accept()

    async def disconnect(self, code=None):
        # if self.convo_id:
        #     await self.channel_layer.group_discard(self.convo_id, self.channel_name)
        #     self.convo_id = None
        pass

    async def receive(self, text_data=None, bytes_data=None):
        data = loads(text_data)

        if self.scope["user"].is_authenticated:
            username = self.scope["user"].username

            if data.get("data_type", None) == "join_chat":
                convo_id = await sync_to_async(get_convo)(username, data.get("friend_username"))
                convo_id = str(convo_id)
                await self.channel_layer.group_add(convo_id, self.channel_name)

            elif data.get("data_type", None) == "leave_chat":
                convo_id = await sync_to_async(get_convo)(username, data.get("friend_username"))
                convo_id = str(convo_id)
                await self.channel_layer.group_discard(convo_id, self.channel_name)

            elif data.get("data_type", None) == "msg_txt":
                def create_msg_model(func_username, data):
                    f_msg_model = Messages()
                    if (USER_MODEL.objects.filter(username=data["recipient"]).exists()) and (data["message_text"]):
                        f_msg_model.sender = Account.objects.get(user__username=func_username)
                        f_msg_model.recipient = Account.objects.get(user__username=data["recipient"])
                        f_msg_model.message_text = data["message_text"]
                        f_msg_model.save()

                        if f_msg_model:
                            f_msg_model_data = {
                                "type": "message",
                                "sender": f_msg_model.sender.user.username,
                                "recipient": f_msg_model.recipient.user.username,
                                "message_text": f_msg_model.message_text,
                                "time_created": f_msg_model.date_created.time().strftime("%H:%M"),
                                "day_created": f_msg_model.date_created.date().strftime("%d-%m-%Y"),

                                "modified_time_created": f_msg_model.date_modified.time().strftime("%H:%M"),
                                "modified_day_created": f_msg_model.date_modified.date().strftime("%d-%m-%Y"),
                            }
                            return f_msg_model_data

                msg_model_data = await sync_to_async(create_msg_model)(username, data)
                convo_id = await sync_to_async(get_convo)(username, data.get("recipient", None))
                convo_id = str(convo_id)
                await self.channel_layer.group_send(convo_id, {
                    "type": "chat.message",
                    "message_data": msg_model_data
                })
                # await self.channel_layer.group_send(self.convo_id, {
                #     "type": "chat.message",
                #     "message_data": msg_model_data
                # })
        else:
            await self.close()

    async def chat_message(self, event):
        message = event.get("message_data", "nothing")
        await self.send(dumps(message))


class ChatSearchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # if not self.scope["user"].is_authenticated:
        #     await self.close()
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        data = loads(text_data)
        search_query = data.get("search_query", None)

        if search_query:
            list_of_acc = await sync_to_async(get_account)(search_query)
            await self.send(dumps(list_of_acc))

        if data.get("type") == "conversation_starter":
            username = self.scope["user"].username
            partner_username = data.get("username", None)
            if partner_username:
                try:
                    if not await sync_to_async(get_convo)(username, partner_username):

                        user_acc = await sync_to_async(Account.objects.get)(user__username=username)
                        partner_acc = await sync_to_async(Account.objects.get)(user__username=partner_username)
                        convo = Conversation(participant_1=user_acc, participant_2=partner_acc)
                        await convo.asave()
                        print("new convo")
                    await self.send(dumps({
                        "type": "conversation_starter",
                        "convo_partner": f"{partner_username}",
                        "outcome": "conversation_created"
                    }))
                except Exception as e:
                    print(e)
                    await self.send(dumps({
                        "type": "conversation_starter",
                        "outcome": "conversation_failed"
                    }))


