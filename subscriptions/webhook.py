from django.utils import timezone
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription, SubscriptionPlan, BookPurchase
from books.models import Books
from django.contrib.auth.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    print('Stripe Signature Header:', sig_header)

    try:
        print('All is ok')
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        print('ValueError:', str(e))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print('SignatureVerificationError:', str(e))
        return HttpResponse(status=400)


    print('Received event:', event['type'])
    print('Timestamp:', event['data']['object']['created'])


    current_time = timezone.now().timestamp()
    event_time = event['data']['object']['created']
    if current_time - event_time > 300:  # Слишком старая временная метка
        print('Слишком старая временная метка события')
        return HttpResponse(status=400)

    # Обработка событий
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return HttpResponse(status=200)

def handle_checkout_session(session):
    customer_email = session.get('customer_email')
    payment_status = session.get('payment_status')
    metadata = session.get('metadata', {})
    purchase_type = metadata.get('purchase_type')

    print(f'Обрабатывается сессия для {customer_email}, статус платежа: {payment_status}, тип покупки: {purchase_type}')

    if payment_status == 'paid':
        if purchase_type == 'subscription':
            # Обработка подписки
            plan_name = session['display_items'][0]['custom']['name']
            plan = SubscriptionPlan.objects.get(name=plan_name)
            user = User.objects.get(email=customer_email)

            # Создание или обновление подписки
            Subscription.objects.update_or_create(
                user=user,
                defaults={'plan': plan, 'start_date': timezone.now(), 'end_date': timezone.now() + timedelta(days=30)}  # Установите срок действия подписки
            )
            print(f'Подписка для {customer_email} на план {plan_name} успешно создана.')

        elif purchase_type == 'book':
            # Обработка покупки книги
            book_id = metadata.get('item_id')
            try:
                book = Books.objects.get(id=book_id)
                user = User.objects.get(email=customer_email)
                BookPurchase.objects.create(user=user, book=book)
                print(f'Книга {book.title} успешно куплена пользователем {customer_email}.')
            except Books.DoesNotExist:
                print(f'Книга с ID {book_id} не найдена.')
            except User.DoesNotExist:
                print(f'Пользователь с email {customer_email} не найден.')
            except Exception as e:
                print(f'Ошибка при обработке покупки книги: {str(e)}')
