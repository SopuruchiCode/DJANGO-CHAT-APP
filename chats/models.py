from django.db import models
from accounts.models import Account
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db.models import Q


class Messages(models.Model):
    message_text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    recipient_group = models.ForeignKey("CustomGroups", on_delete=models.SET_NULL, null=True, blank=True, related_name="recieving_groups")

    def is_group_message(self):
        return bool(self.recipient_group)

    def save(self, *args, **kwargs):
        if self.recipient and self.recipient_group:
            raise ValidationError("recipient and recipient_group cannot be set at the same time")
        super(Messages, self).save(*args, **kwargs)

        if self.recipient:
            participants_list = [self.sender, self.recipient]
            convo_queryset = Conversation.objects.filter(participant_1__in=participants_list, participant_2__in=participants_list)
            if convo_queryset.exists() and convo_queryset.count() == 1:
                convo = convo_queryset.first()
                convo.add_message(self)
                convo.save()

            else:
                convo = Conversation()
                convo.participant_1 = self.sender
                convo.participant_2 = self.recipient
                convo.save()
                convo.messages.add(self)
                convo.save()

    def __str__(self):
        return f'{self.id}'


class Conversation(models.Model):
    participant_1 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="participant1_convo")
    participant_2 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="participant2_convo")
    messages = models.ManyToManyField(Messages)
    timestamp = models.DateTimeField(auto_now=True)

    def add_message(self, msg_to_add):
        if msg_to_add.is_group_message():
            raise ValidationError('Group_messages can not be added to a private conversation')

        participant_list = [self.participant_1, self.participant_2]

        if msg_to_add.sender in participant_list and msg_to_add.recipient in participant_list:
            self.messages.add(msg_to_add)
            self.save()
        else:
            raise ValidationError("Message must be related to the conversation's participants")

    def last_message(self):
        try:
            last_msg = self.messages.all().order_by("-date_created")[0]                        #Newest date first
            return last_msg
        except IndexError:
            return None    #no messages have been sent


    def __str__(self):
        return f"{self.participant_1} <--> {self.participant_2}"

    # def add_message(self, message_id):                                       Deprecated because of the schema change
    #     try:
    #         message_id = int(message_id)
    #     except Exception:
    #         raise ValidationError("message_id is not a valid number")
    #     if Messages.objects.filter(id=message_id).exists():
    #         message = Messages.objects.get(id=message_id)
    #         participant_ids = [self.participant_1.user.id, self.participant_2.user.id]
    #         if message.is_group_message():
    #             raise ValidationError("Group messages cant be added to private conversations")
    #
    #         if (message.sender.user.id in participant_ids) and (message.recipient.user.id in participant_ids):
    #             self.message_list.append(message_id)
    #             self.save()
    #         else:
    #             raise ValidationError("This message is no between the participants")
    #
    #     else:
    #         raise ValidationError("Message does not exist")

    # def last_message(self):                                                    Deprecated because of the schema change
    #     last_msg_id = self.message_list[-1]
    #     if Messages.objects.filter(id=last_msg_id).exists():
    #         return Messages.objects.get(id=last_msg_id)
    #
    #     return None


def group_image(instance, filename):
    name = instance.name
    g_id = instance.id
    this_day = datetime.now().strftime("%Y_%m_%d--%H:%M:%S")
    file_details = "".join(filename.split("."))
    file_name = file_details[0]
    ext = file_details[-1]
    return f'groups/{name}-{g_id}/{file_name}---{this_day}.{ext}'


class CustomGroups(models.Model):
    name = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to=group_image, default="defaults/profile_pic/default-profile-pic.png")
    admin = models.ForeignKey(Account, models.SET_NULL, null=True, related_name="admin_custom_group")
    date_created = models.DateTimeField(auto_now_add=True)
    max_member_no = models.IntegerField(default=8)
    members = models.ManyToManyField(Account, related_name="member_custom_group")
    messages = models.ManyToManyField(Messages)
    timestamp = models.DateTimeField(auto_now=True)

    def last_message(self):
        try:
            last_msg = self.messages.all().order_by("-date_created")[0]             #Newest date first
            return last_msg
        except IndexError:
            return None    #no messages have been sent

    def __str__(self):
        return f"{self.id}:::{self.name}"
    
    def save(self, *args, **kwargs):
        if self.members.count() > self.max_member_no:
            raise ValidationError("Max members exceeded")
        super().save(*args, **kwargs)
