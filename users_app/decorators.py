from django.shortcuts import redirect


def user_is_authenticated(view):
    """ Проверяем, авторизирован ли пользователь на сайте """

    def wrapper(requset, *args, **kwargs):
        if requset.user.is_authenticated:
            return redirect('users_app:homepage')
        else:
            return view(requset, *args, **kwargs)

    return wrapper
