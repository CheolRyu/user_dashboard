from __future__ import unicode_literals

from django.db import models
import re
import bcrypt
import time
import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.

def num_check(name): #checks if name contains number
    contains_num = False
    for char in name:
        if char.isdigit():
            contains_num = True
        return contains_num

def contains_upper_num(password): #checks if the entered password meets our requirements
    contains_upper = False
    contains_num = False
    check = False
    
    for char in password:
        if char.isupper():
            contains_upper = True
        elif char.isdigit():
            contains_num = True
        
    if contains_num and contains_upper:
        check = True

    return check



class UserManager(models.Manager):
    def regi_validation(self, post_data):
        print post_data
        errors = {}

        for item in post_data:
            print item

            if len(post_data[item]) < 1:
                errors['submit'] = "All fields required" 
                return (True, errors)

            if len(post_data[item]) > 255:
                errors[item] = "Exceeded field length"
                return (True, errors)
            print errors

            if len(post_data['first_name']) < 2:
                errors['first_name'] = "First name should be more than 2 characters."
            if len(post_data['last_name']) < 2: 
                errors['last_name'] = "Last name should be more than 2 characters."
            if num_check(post_data['first_name']):
                errors['first_name'] = "Names must only contain letters"
            if num_check(post_data['last_name']):
                errors['last_name'] = "Names must only contain letters"
            if not EMAIL_REGEX.match(post_data['email']):
                errors["email"] = "Invalid email address"
            if len(post_data['pwd']) < 8:
                errors["pwd"] = "Password must be at least 8 characters"
            if not contains_upper_num(post_data['pwd']):
                errors["pwd"] = "Password must contain at least one uppercase letter and one number"
            if post_data['confirm_pwd'] != post_data['pwd']:
                errors["confirm_pwd"] = "Passwords must match"

            records = User.objects.filter(email=post_data['email']) # lets store existing user to records
            
            if len(records) > 0: #iterate through and look for it
                errors["email"] = "Email in use!"
            print errors

            if len(errors) > 0: #return errors if there is errors
                return (True,errors)
            else: #otherwise, convert pwd to bcrypt pwd and store users to DB
                new_pwd = bcrypt.hashpw(post_data['pwd'].encode(), bcrypt.gensalt())
                new_user = User.objects.create(email=post_data['email'], first_name=post_data['first_name'], last_name=post_data['last_name'], password=new_pwd)
                new_id = new_user.id
                return (False,new_id)

    def login_validation(self, post_data):
        errors = {}
        for item in post_data:
            print(post_data[item])
            if len(post_data[item]) < 1:
                errors[item] = "All fields required"
                return (True, errors)
            if len(post_data[item]) > 225:
                errors[item] = "Exceeded field length"
                return (True, errors)

        records = User.objects.filter(email=post_data['email'])

        if len(records) > 0:
            pwd = records[0].password
            check = bcrypt.checkpw(post_data['pwd'].encode(), pwd.encode())
            if check:
                return (False, records[0].id)
            else:
                errors["pwd"] = "Incorrect user/password"
                return (True, errors)
        else:
            errors["email"] = "Account doesn't exist for this email. Please register."
            return (True, errors)

    def update_validaiton(request, post_data, user_id):
        errors = {}
        for item in post_data:
            if len(post_data[item]) < 1:
                errors['submit'] = "All fields required"

            if len(post_data[item]) > 225:
                errors[item] = "Exceeded field length"

        if len(errors) > 0:
            return (True, errors)
            print post_data['type']


        if post_data['type'] == 'information':
            if len(post_data['first_name']) < 2:
                errors['first_name'] = "Name should be more than 2 characters"
            if len(post_data['last_name']) < 2:
                errors['first_name'] = "Name should be more than 2 characters"
            if num_check(post_data['first_name']):
                errors['first_name'] = "Names must only contain letters"
            if num_check(post_data['last_name']):
                errors['first_name'] = "Names must only contain letters"

            if not EMAIL_REGEX.match(post_data['email']):
                errors["email"] = "Invalid email address"

            records = User.objects.filter(email=post_data['email'])
            if len(records) > 0:
                errors["email"] = "Account already exists for this email"
            if len(errors) > 0:
                return (True, errors)

            edit_user = User.objects.get(id=user_id)
            edit_user.first_name = post_data['first_name']
            edit_user.last_name = post_data['last_name']
            edit_user.email = post_data['email']
            edit_user.save()
            return (False, "Successfully updated information")

        elif post_data['type'] == 'password':
            if len(post_data['pwd']) < 8:
                errors["pwd"] = "Password must be at least 8 characters"
            if not contains_upper_num(post_data['pwd']):
                errors["pwd"] = "Password must contain at least one uppercase letter and one number"
            if post_data['confirm_pwd'] != post_data['pwd']:
                errors["confirm_pwd"] = "Passwords must match"
            if len(errors) > 0:
                return (True, errors)

            new_pwd = bcrypt.hashpw(post_data['pwd'].encode(), bcrypt.gensalt())
            edit_user = User.objects.get(id=user_id)
            edit_user.password = new_pwd
            edit_user.save()
            return (False, "Successfully updated password")

        elif post_data['type'] == 'description':
            edit_user = User.objects.get(id=user_id)
            print edit_user
            edit_user.desc = post_data['desc']
            edit_user.save()
            return (False, "Successfully updated description")
        else:
            errors['type'] = "Processing error. Invalid submission."
            return (True, errors)


    def admin_update_validations(request, post_data, user_id):
        errors = {}
        for item in post_data:
            if len(post_data[item]) < 1: 
                errors['submit'] = "All fields required"
            if len(post_data[item]) > 225:
                errors[item] = "Exceeded field length"

        if len(errors) > 0:
            return (True, errors)


        if post_data['type'] == 'information':
            if len(post_data['first_name']) < 2:
                errors['first_name'] = "Name must be longer than 2 characters"
            if len(post_data['last_name']) < 2:
                errors['last_name'] = "Name must be longer than 2 characters"
            if num_check(post_data['first_name']):
                errors['first_name'] = "Names must only contain letters"
            if num_check(post_data['last_name']):
                errors['first_name'] = "Names must only contain letters"
            if not EMAIL_REGEX.match(post_data['email']):
                errors["email"] = "Invalid email address"
            records = User.objects.filter(email=post_data['email'])

            if len(records) > 0:
                if records[0].email != post_data['email']:
                    errors["email"] = "Account already exists for this email"

            if post_data['user_level'] != 'normal' and post_data['user_level'] != 'admin':
                errors['user_level'] = "Invalid user level entered"
            
            if len(errors) > 0:
                return (True, errors)

            print post_data

            edit_user = User.objects.get(id=user_id)
            edit_user.first_name = post_data['first_name']
            edit_user.last_name = post_data['last_name']
            edit_user.email = post_data['email']
            edit_user.user_level = post_data['user_level']
            edit_user.save()
            print edit_user.user_level
            return (False, "Successfully updated information")

        elif post_data['type'] == 'password':
            if len(post_data['pwd']) < 8:
                errors["pwd"] = "Password must be at least 8 characters"
            if not contains_upper_num(post_data['pwd']):
                errors["pwd"] = "Password must contain at least one uppercase letter and one number"
            if post_data['confirm_pwd'] != post_data['pwd']:
                errors["confirm_pwd"] = "Passwords must match"
            if len(errors) > 0:
                return (True, errors)

            new_pwd = bcrypt.hashpw(post_data['pwd'].encode(), bcrypt.gensalt())
            edit_user = User.objects.get(id=user_id)
            edit_user.password = new_pwd
            edit_user.save()
            return (False, "Successfully updated password")

class MessageManager(models.Manager):
    def message_validation(self, post_data, user_id, session_id):
        errors = {}
        for item in post_data:
            if len(post_data[item]) < 1:
                errors['submit'] = "Message field blank"
            if len(post_data[item]) > 255:
                errors[item] = "Exceeded field length"

        if len(errors) > 0:
            return (True, errors)

        new_message = Message.objects.create(message=post_data['message'])
        rel_receiver = User.objects.get(id=user_id)
        rel_poster = User.objects.get(id=session_id)
        new_message.receiver = rel_receiver
        new_message.poster = rel_poster
        new_message.save()
        return (False, "Successfully updated information")

    def delete_messages(self, user_id):
        get_messages = Message.objects.filter(poster=user_id)
        if len(get_messages) > 0:
            get_messages.delete()
            return(True, "Successfully deleted messages")

        else:
            return(False, "Couldn't delete messages")


class CommentManager(models.Manager):
    def comment_validation(self, post_data, user_id):
        errors = {}
        for item in post_data:
            if len(post_data[item]) < 1:
                errors['submit'] = "Comment field blank"
            if len(post_data[item]) > 255:
                errors[item] = "Exceeded field length"

        if len(errors) > 0:
            return (True, errors)

        new_comment = Comment.objects.create(comment=post_data['comment'])
        rel_msg = Message.objects.get(id=post_data['rel_message'])
        rel_commentor = User.objects.get(id=user_id)
        new_comment.message = rel_msg
        new_comment.commentor = rel_commentor
        new_comment.save()
        return (False, "Successfully updated information")

    def delete_comments(self, user_id):
        get_comments = Comment.objects.filter(commentor=user_id)
        print get_comments
        if len(get_comments) > 0:
            get_comments.delete()
            return(True, "Successfully deleted comments")

        else:
            return(False, "Couldn't delete comments")


class User(models.Model):
    email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    user_level = models.CharField(max_length=10,default='normal')
    desc = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __repr__(self):
        return "<User object: id='{}' email='{}' first_name='{}' last_name='{}' user_level='{}' desc='{}' created='{}'>".format(self.id, self.email, self.first_name, self.last_name, self.user_level, self.desc, self.created_at)


class Message(models.Model):
    message = models.CharField(max_length=225)
    poster = models.ForeignKey(User, related_name="messages_posted", null=True)
    receiver = models.ForeignKey(User, related_name="messages_received", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MessageManager()

    def __repr__(self):
        return "<Message object: id='{}' message='{}' poster='{}' receiver='{}' created='{}'>".format(self.id, self.message, self.poster, self.receiver, self.created_at)



class Comment(models.Model):
    comment = models.CharField(max_length=225)
    message = models.ForeignKey(Message, related_name='comments', null=True)
    commentor = models.ForeignKey(User, related_name='comments_posted', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CommentManager()

    def __repr__(self):
        return "<Comment object: id='{}' comment='{}' message='{}' commentor='{}' created='{}'>".format(self.id, self.comment, self.message, self.commentor, self.created_at)