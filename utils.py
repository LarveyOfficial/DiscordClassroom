import discord
import config


def get_profile(user_id):
    document = config.USERS.find_one({'user_id': user_id})
    if document is None:
        document = {'user_id': user_id, 'is_student': True, 'google_classroom': None, 'bio': None, 'classes': [], 'teacher_notifications': True, 'student_notifications': True}
        config.USERS.insert_one(document)
        return document, True
    return document, False
