from django.urls import path
from . import views
from . import webhook

app_name = 'subscriptions'

urlpatterns = [
    path('subscriptions-list/', views.SubscriptionsList.as_view(), name='subscriptions_list'),
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    path('create-subscription-session/<int:plan_id>/', views.create_subscription_session,
         name='create_subscription_session'),
    path('create-book-purchase-session/<int:book_id>/', views.create_book_purchase_session,
         name='create_book_purchase_session'),
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
    path('webhook/', webhook.stripe_webhook),
    path('plans/', views.SubscriptionPlanViewSet.as_view({'get': 'list'}), name='plan-list'),

]
