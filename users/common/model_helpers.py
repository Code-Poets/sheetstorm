from users import models


def create_user_using_full_clean_and_save(email, first_name, last_name, phone_number, password):
    user = models.CustomUser(email=email, first_name=first_name, last_name=last_name, phone_number=phone_number)
    user.set_password(password)
    user.full_clean()
    user.save()
    return user
