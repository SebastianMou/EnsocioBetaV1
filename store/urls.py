from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('inicio/', views.home_front, name='home_front'),
    path('user_login/', views.user_login, name='user_login'),
    path('buyer_register/', views.buyer_register, name='buyer_register'),
    path('seller_register/SVZOMGHDICY27X5-YWB5LZF2O3KXPSI-KI45BDEYRSQ0LFT-ELOWF93S846ATVQ/', views.seller_register, name='seller_register'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('profile/', views.profile, name='profile'),
    path('visible_profile/<str:username>/', views.visible_profile, name='visible_profile'),

    path('inbox/', views.inbox, name='inbox'),
    path('directs/<str:username>/', views.directs, name='directs'),
    path('send_message_ajax/', views.send_message_ajax, name='send_message_ajax'),
    path('get_messages_ajax/<str:username>/', views.get_messages_ajax, name='get_messages_ajax'),
    path('delete_conversation_ajax/<str:username>/', views.delete_conversation, name='delete_conversation'),
    
    # Controlling post
    path('create_post/', views.create_post, name='create_post'),
    path('all_posts/', views.all_posts, name='all_posts'),
    path('post_detail/<int:pk>/', views.post_detail, name='post_detail'),

    path('posts/<int:pk>/like/', views.post_like, name='post_like'),
    path('posts/<int:pk>/dislike/', views.post_dislike, name='post_dislike'),
    path('comment_delete/<int:pk>/', views.comment_delete, name='comment_delete'),
    path('post/<int:post_id>/favorite/', views.favorite_view, name='post_favorite'),

    path('edit_post/<int:pk>/', views.edit_post, name='edit_post'),
    path('delete/<int:post_id>/', views.delete, name='delete'),
    path('search/', views.search, name='search'),
    path('category_list/<int:pk>', views.category_list, name='category_list'),

    # Stripe Payment connection
    path('create_checkout_session/<int:pk>/', views.create_checkout_session, name='create_checkout_session'),
    path('checkout_success/', views.checkout_success, name='checkout_success'),
    path('checkout_cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('transactions/', views.transaction_list, name='transaction_list'),

    # activación de la cuenta de usuario por correo electrónico
    path('activate/<uidb64>/<token>', views.activate, name='activate'),

    # User change password from account 
    path('change_password/', login_required(auth_views.PasswordChangeView.as_view(template_name='authentication/password_change.html', success_url='/password_changed/')), name='password_change'),
    path('password_changed/', login_required(auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_changed.html')), name='password_changed'),    
    # Forgoten password
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), name="password_reset"),
    path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="authentication/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'), name='password_reset_complete'),      
    
    # Forgoten password
    path('admin_only/', views.admin_only, name='admin_only'),
    path('conversation/<str:username1>/<str:username2>/', views.specific_user_conversation, name='specific_user_conversation'),
    path('admin_only_search_user_convo/', views.admin_only_search_user_convo, name='admin_only_search_user_convo'),
]