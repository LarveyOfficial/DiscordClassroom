import discord
import config


def get_profile(user_id):
    document = config.USERS.find_one({'user_id': user_id})
    if document is None:
        document = {'user_id': user_id, 'premium': False, 'is_student': True, 'google_classroom': None, 'note': None, 'classes': [], 'teacher_notifications': True, 'student_notifications': True}
        config.USERS.insert_one(document)
        return document, True
    return document, False


def get_user_classes(user_id):
    return config.CLASSES.find({'members': user_id})


def get_teaching_classes(user_id):
    return config.CLASSES.find({'owner': user_id})
