from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import (CreateUserAPIView,
                    UpdateDeleteUserAPIView,
                    CreateHairdresserAPIView,
                    AddPhotoToPortfolioAPIView,
                    GetHairdresserAPIView,
                    UpdateDeleteHairdresserAPIView,
                    SelectionAPIView,
                    GetCommentsAPIView,
                    AddCommentAPIview,
                    SkillsAPIView,
                    RegionsAPIView,
                    CitiesAPIView,
                    GetCityAPIView,
                    GetAllCitiesInTheRegion,
                    RemovePhotoFromPortfolio,
                    ChangePasswordView,
                    AddAvatarAPIView,
                    DeleteAvatarAPIView)

app_name = 'drf_app'
urlpatterns = [
    # users
    path('create_user/', CreateUserAPIView.as_view()),
    path('add_avatar/', AddAvatarAPIView.as_view()),
    path('delete_avatar/', DeleteAvatarAPIView.as_view()),
    path('update_delete_user/', UpdateDeleteUserAPIView.as_view()),
    path('create_hairdresser/', CreateHairdresserAPIView.as_view()),
    path('add_photo_to_portfolio/', AddPhotoToPortfolioAPIView.as_view()),
    path('remove_all_photo_from_portfolio/', RemovePhotoFromPortfolio.as_view()),
    path('get_hairdresser/<slug:username>/', GetHairdresserAPIView.as_view()),
    path('update_delete_hairdresser/', UpdateDeleteHairdresserAPIView.as_view()),
    # change password
    path('change_password/', ChangePasswordView.as_view()),
    # selection
    path('selection/', SelectionAPIView.as_view()),
    # comments
    path('comments/<slug:username>/', GetCommentsAPIView.as_view()),
    path('add_comment/<slug:username>/', AddCommentAPIview.as_view()),
    # other
    path('get_skills/', SkillsAPIView.as_view()),
    path('get_regions/', RegionsAPIView.as_view()),
    path('get_cities/', CitiesAPIView.as_view()),
    path('get_city/<int:pk>/', GetCityAPIView.as_view()),
    path('get_cities_in_the_region/<int:pk>/', GetAllCitiesInTheRegion.as_view()),
    # jwt
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
