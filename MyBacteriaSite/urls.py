from django.urls import path
from . import views

app_name = "MyBacteriaSite"   


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("gallery", views.gallery, name= "gallery"),
    path("report_pdf", views.report_pdf, name= "report_pdf"),
    # path('posts-positions/', views.posts_positions, name='posts-positions/'),

    path("microbe_list", views.microbe_list, name= "microbe_list"),
    path("add_microbe", views.add_microbe, name= "add_microbe"),
    path("edit_microbe/<str:pk>/", views.edit_microbe, name= "edit_microbe"),
    path("delete_microbe/<str:pk>/", views.delete_microbe, name= "delete_microbe"),
    path("microbes_as_csv", views.microbes_as_csv, name= "microbes_as_csv"),

    
    path("show_post/<str:pk>/", views.show_post, name= "show_post"),
    path("like_post/<int:pk>/", views.like_post, name= "like_post"),
    path("add_post", views.add_post, name= "add_post"),
    path("edit_post/<str:pk>/", views.edit_post, name= "edit_post"),
    path("delete_post/<str:pk>/", views.delete_post, name= "delete_post"),

    path("profile", views.profile, name= "profile"),
    path("edit_profile", views.edit_profile, name= "edit_profile"),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout")
]