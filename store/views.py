from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .tokens import account_activation_token

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest

from .forms import (UserSellerRegisterForm, UserBuyerRegisterForm, PostForm, UserUpdateForm, 
                    ProfileUpdateForm, UpdatePostForm, CommentForm, ReplyForm, PasswordConfirmationForm,
                    OfferForm)
from .models import Post, Category, Profile, Comment, CartItem, Message, Transaction, Offer

import stripe
import logging
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def home(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')
        subject = request.POST.get('subject')
        name = request.POST.get('name')
        data = {
            'complaint': 'ENSOCIO.MX',
            'name': name,
            'subject': subject,
            'email': email,
            'message': message, 
        }
        message = '''
        From: {}
        Email: {}
        New message: {}
        '''.format(data['name'], data['email'], data['message'])
        send_mail(data['complaint'], message, '', ['ensocio.mx@gmail.com'])

    categories = Category.objects.filter(
        Q(name__startswith='Servicios de voz') | Q(name__startswith='Diseño gráfico') |
        Q(name__startswith='Servicios de SEO')
    )[:3]
    context = {
        'categories': categories,
    }
    return render(request, 'home.html', context)

def home_front(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')
        subject = request.POST.get('subject')
        name = request.POST.get('name')
        data = {
            'complaint': 'ENSOCIO.MX',
            'name': name,
            'subject': subject,
            'email': email,
            'message': message, 
        }
        message = '''
        From: {}
        Email: {}
        New message: {}
        '''.format(data['name'], data['email'], data['message'])
        send_mail(data['complaint'], message, '', ['ensocio.mx@gmail.com'])

    categories = Category.objects.filter(
        Q(name__startswith='Servicios de voz') | Q(name__startswith='Diseño gráfico') |
        Q(name__startswith='Servicios de SEO')
    )[:3]
    context = {
        'categories': categories,
    }
    return render(request, 'home_front.html', context)

def category_list(request, pk):
    if request.method == 'POST':
        query = request.POST.get('search' )
        results = Post.objects.filter(title__icontains=query)

        categories = Category.objects.all()
        category = get_object_or_404(Category, pk=pk)

        posts_list = Post.objects.filter(category=category)
        paginator = Paginator(posts_list, 50)
        page_number = request.GET.get("page")
        posts = paginator.get_page(page_number)

        context = {
            'categories': categories,
            'category': category,
            'posts': posts,
            'results': results,
        }
        return render(request, 'service/category.html', context)
    else:
        categories = Category.objects.all()
        category = get_object_or_404(Category, pk=pk)
        posts_list = Post.objects.filter(category=category)
        paginator = Paginator(posts_list, 50)
        page_number = request.GET.get("page")
        posts = paginator.get_page(page_number)
        context = {
            'categories': categories,
            'category': category,
            'posts': posts,
        }
        return render(request, 'service/category.html', context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'contraseña o nombre de usuario incorrecto')
            return redirect('user_login')
    else:
        pass
    return render(request, 'autho/user_login.html')

def email_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Try to get a user with the provided email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Email not found')
            return redirect('email_login')

        # Authenticate the user
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Invalid password')
            return redirect('email_login')

    return render(request, 'autho/email_login.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        form = PasswordConfirmationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=request.user.username, password=password)
            if user is not None:
                request.user.delete()
                messages.success(request, 'Su cuenta ha sido eliminada.')
                return redirect('home_front')
            else:
                messages.error(request, 'Contraseña incorrecta. Por favor, inténtelo de nuevo.')
    else:
        form = PasswordConfirmationForm()
    return render(request, 'autho/delete_account.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home_front')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Gracias por confirmar su correo electrónico. Ahora puede iniciar sesión en su cuenta.')
        return redirect('user_login')
    else:
        messages.error(request, 'El enlace de activación no es válido!')
    
    return render(request, 'home.html')

def activateEmail(request, user, to_email):
    mail_subject = 'Active su cuenta de usuario.'
    message = render_to_string('authentication/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Estimado/a {user}, por favor vaya a su correo {to_email} y haga clic en \
            el enlace de activación que ha recibido para confirmar y completar el registro. Nota: Revise su carpeta de spam.')
    else:
        messages.error(request, f'Problema enviando correo de confirmación a {to_email}, verifique si lo escribió correctamente.')


def seller_register(request):
    if request.method == 'POST':
        form = UserSellerRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered.')
                return redirect('seller_register')
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                activateEmail(request, user, form.cleaned_data.get('email'))
                return redirect('home_front')
    else:
        form = UserSellerRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'autho/seller_register.html', context)


def activate_buyer(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Gracias por confirmar su correo electrónico. Ahora puede iniciar sesión en su cuenta.')
        return redirect('user_login')
    else:
        messages.error(request, 'El enlace de activación no es válido!')
    return render(request, 'home.html')

def activateEmail_buyer(request, user, to_email):
    mail_subject = 'Active su cuenta de usuario.'
    message = render_to_string('authentication/template_activate_account_buyer.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Estimado/a {user}, por favor vaya a su correo {to_email} y haga clic en \
            el enlace de activación que ha recibido para confirmar y completar el registro. Nota: Revise su carpeta de spam.')
    else:
        messages.error(request, f'Problema enviando correo de confirmación a {to_email}, verifique si lo escribió correctamente.')


def buyer_register(request):
    if request.method == 'POST':
        form = UserBuyerRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Este correo electrónico ya está registrado.')
                return redirect('buyer_register')
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                activateEmail_buyer(request, user, form.cleaned_data.get('email'))
                return redirect('home_front')
    else:
        form = UserBuyerRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'autho/buyer_register.html', context)

@csrf_protect
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if hasattr(request.user, 'account') and request.user.account.freelancer_key:
                post.author = request.user
                post.save()
                return redirect('post_detail', pk=post.pk)
            else:
                form.add_error(None, 'Debe tener un número de clave de freelancer para crear una publicación.')
    else:
        form = PostForm()
    return render(request, 'service/create_posts.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    if post.author != request.user:
        return redirect('home_front')

    if request.method == 'POST':
        form = UpdatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(reverse('post_detail', args=[post.pk]))
    else:
        form = UpdatePostForm(instance=post)
    context = {
        'form': form,
    }
    return render(request, 'service/edit_post.html', context)

@login_required
def delete(request, post_id=None):
    post = Post.objects.get(id=post_id)
    if post.author != request.user:
        return redirect('home_front')
    post.delete()
    return redirect('profile')

def all_posts(request):
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, 50)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    categories_list = Category.objects.all()
    paginator_category = Paginator(categories_list, 70)
    page_number = request.GET.get("page")
    categories = paginator_category.get_page(page_number)

    context = {
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'service/all_posts.html', context)

def post_detail(request, pk):
    product = get_object_or_404(Post, pk=pk)
    comments_list = product.comment_set.filter(parent__isnull=True)
    paginator = Paginator(comments_list, 50)
    page_number = request.GET.get("page")
    comments = paginator.get_page(page_number)
    cout_reviews = Comment.objects.filter(product=product).count()
    # current_url = request.build_absolute_uri()
    related_products = product.related_products()

    if request.user.is_authenticated:
        is_favorite = product.cartitem_set.filter(user=request.user).exists()
    else:
        is_favorite = None

    if request.method == 'POST':
        form = CommentForm(request.POST)
        reply_form = ReplyForm(request.POST)
        if 'comment_id' in request.POST:  # processing a reply
            comment = get_object_or_404(Comment, pk=request.POST['comment_id'])
            reply = reply_form.save(commit=False)
            reply.product = product
            reply.author = request.user
            reply.parent = comment
            reply.save()
            return redirect('post_detail', pk=pk)  # redirect back to the same page after replying
        elif form.is_valid():  # processing a new top-level comment
            comment = form.save(commit=False)
            comment.product = product
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=pk)  # redirect back to the same page after commenting
    else:
        form = CommentForm()
        reply_form = ReplyForm()
    context = {
        'product': product,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'comments': comments,
        'form': form,
        'reply_form': reply_form,
        'cout_reviews': cout_reviews,
        'is_favorite': is_favorite,
        # 'current_url': current_url,
        'related_products': related_products,
    }
    return render(request, 'service/post_detail.html', context)

def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST' and request.user == comment.author:
        comment.delete()
        messages.success(request, 'Comentario eliminado con éxito.')
    else:
        messages.error(request, 'No se puede eliminar el comentario.')
    return redirect('post_detail', pk=comment.product.pk)

def create_checkout_session(request, pk):
    product = get_object_or_404(Post, pk=pk)
    ng = "https://ensocio.herokuapp.com"
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        quantity = int(request.POST.get('quantity', 1))
        name = f"{product.author} - {product.title}"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'mxn',
                        'unit_amount': product.price,
                        'product_data': {
                            'name': name,
                            'description': product.category,
                        },
                    },
                    'quantity': quantity,
                },
            ],
            mode='payment',
            success_url=ng + '/checkout_success',
            cancel_url=ng + '/checkout_cancel',
            metadata={
                'post_id': product.id,
                'seller_id': product.author.id,
                'buyer_id': request.user.id,
                'quantity': quantity,
            },
        )
        return redirect(checkout_session.url)
    else:
        return JsonResponse({'error': 'Invalid request method'})

def post_like(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        post.dislikes.remove(request.user)
    return redirect('post_detail', pk=post.id)

def post_dislike(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
    else:
        post.dislikes.add(request.user)
        post.likes.remove(request.user)
    return redirect('post_detail', pk=post.id)

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    print("Webhook called")
    if "HTTP_STRIPE_SIGNATURE" not in request.META:
        logger.error(f"Missing Stripe signature. Headers: {request.META}")
        return HttpResponseBadRequest("Missing Stripe signature")

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    print(f"Event: {event}")

    if event['type'] == 'checkout.session.completed':
        print("Handling checkout.session.completed event")
        session = event['data']['object']
        post_id = session['metadata']['post_id']
        seller_id = session['metadata']['seller_id']
        buyer_id = session['metadata']['buyer_id']
        quantity = session['metadata']['quantity']

        post = Post.objects.get(id=post_id)
        seller = User.objects.get(id=seller_id)
        buyer = User.objects.get(id=buyer_id)

        transaction = Transaction(
            buyer=buyer,
            seller=seller,
            post=post,
            quantity=quantity,
            amount=session['amount_total']
        )
        transaction.save()
        print(f"Transaction saved: {transaction}")
        logger.info(f"Transaction saved: {transaction}")

    else:
        logger.warning(f"Received an unhandled event: {event}")

    return HttpResponse(status=200)

@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-created_at')
    return render(request, 'transactions/list.html', {'transactions': transactions})

def checkout_success(request):
    return render(request, 'checkout_success.html')

def checkout_cancel(request):
    return render(request, 'checkout_cancel.html')

def search(request):
    query = request.GET.get('search', '')

    results_list = Post.objects.filter(title__icontains=query)
    paginator = Paginator(results_list, 50)
    page_number = request.GET.get("page")
    results = paginator.get_page(page_number)

    results_c_list = Category.objects.filter(name__icontains=query)
    paginator_c = Paginator(results_c_list, 50)
    page_number_c = request.GET.get("page")
    results_c = paginator_c.get_page(page_number_c)

    context = {
        'results': results,
        'query': query,
        'results_c': results_c,
    }
    return render(request, 'service/search.html', context)

@login_required
def profile(request):
    posts_list = Post.objects.filter(author=request.user)
    paginator_posts = Paginator(posts_list, 10)  # Show 10 contacts per page.
    page_number_of_post = request.GET.get("page")
    posts = paginator_posts.get_page(page_number_of_post)

    favorite_posts = CartItem.objects.filter(user=request.user).values_list('post', flat=True)
    cart_items_list = Post.objects.filter(id__in=favorite_posts)
    paginator = Paginator(cart_items_list, 10)
    page_number_of_cart_items = request.GET.get("page")
    cart_items = paginator.get_page(page_number_of_cart_items)

    post_count = Post.objects.filter(author=request.user).count()
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        profile, created = Profile.objects.get_or_create(user=request.user)  # If the switch is True, that means Django had to create a new Profile object for the user because it couldn't find an existing one
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'not loged-in')
            # get all comments on user's posts
            comments_list = Comment.objects.filter(product__author=request.user)
            paginator_comments_list = Paginator(comments_list, 20)
            page_number_of_comments = request.GET.get("page")
            comments = paginator_comments_list.get_page(page_number_of_comments)

            comments_reply_post_list = Comment.objects.filter(parent__author=request.user)
            paginator_comments_reply_post = Paginator(comments_reply_post_list, 20)
            page_number_of_comments_reply_post = request.GET.get("page")
            comments_reply_post = paginator_comments_reply_post.get_page(page_number_of_comments_reply_post)
            
            context = {
                'u_form': u_form,
                'p_form': p_form,
                'posts': posts,
                'post_count': post_count,
                'cart_items': cart_items,
                'comments': comments, 
                'comments_reply_post': comments_reply_post,
            }
            return render(request, 'autho/profile.html', context)
    else: 
        u_form = UserUpdateForm(instance=request.user)
        profile, created = Profile.objects.get_or_create(user=request.user)
        p_form = ProfileUpdateForm(instance=profile)
        
    # get all comments on user's posts
    comments_list = Comment.objects.filter(product__author=request.user)
    paginator_comments_list = Paginator(comments_list, 20)
    page_number_of_comments = request.GET.get("page")
    comments = paginator_comments_list.get_page(page_number_of_comments)

    comments_reply_post_list = Comment.objects.filter(parent__author=request.user)
    paginator_comments_reply_post = Paginator(comments_reply_post_list, 20)
    page_number_of_comments_reply_post = request.GET.get("page")
    comments_reply_post = paginator_comments_reply_post.get_page(page_number_of_comments_reply_post)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'posts': posts,
        'post_count': post_count,
        'cart_items': cart_items,
        'comments': comments,
        'comments_reply_post': comments_reply_post,
    }
    return render(request, 'autho/profile.html', context)

def favorite_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    favorite, created = CartItem.objects.get_or_create(user=request.user, post=post)
    if not created:
        favorite.delete()
    return redirect('post_detail', pk=post.pk)

def visible_profile(request, username):
    user = get_object_or_404(User, username=username)

    favorite_posts = CartItem.objects.filter(user=user).values_list('post', flat=True)
    cart_items_list = Post.objects.filter(id__in=favorite_posts)
    paginator = Paginator(cart_items_list, 10)
    page_number_of_cart_items = request.GET.get("page")
    cart_items = paginator.get_page(page_number_of_cart_items)

    posts_list = Post.objects.filter(author=user)
    paginator_posts = Paginator(posts_list, 10)
    page_number_of_posts = request.GET.get("page")
    posts = paginator_posts.get_page(page_number_of_posts)


    post_count = Post.objects.filter(author=user).count()

    last_login = user.last_login
    current_time = timezone.now()
    if request.user == user:
        show_chat_button = False
    else:
        show_chat_button = True
    if current_time - last_login < timezone.timedelta(minutes=5):
        is_active = True
    else:
        is_active = False

    context = {
        'user': user,
        'posts': posts,
        'post_count': post_count,
        'is_active': is_active,
        'show_chat_button': show_chat_button,
        'favorite_posts': favorite_posts,
        'cart_items': cart_items,
    }
    return render(request, 'autho/visible_profile.html', context)

# @login_required
# def inbox(request):
#     user = request.user
#     messages = Message.get_message(user=user)
#     active_direct = None
#     directs = None

#     if messages:
#         message = messages[0]
#         active_direct = message['user'].username
#         directs = Message.objects.filter(user=user, reciepient=message['user'])
#         directs.update(is_read=True)

#         for message in messages:
#             if message['user'].username == active_direct:
#                 message['unread'] = 0

#     last_login = user.last_login
#     current_time = timezone.now()
#     if current_time - last_login < timezone.timedelta(minutes=5):
#         is_active = True
#     else:
#         is_active = False

#     context = {
#         'directs': directs,
#         'active_direct': active_direct,
#         'messages': messages,
#         'is_active': is_active,
#     }
#     return render(request, 'autho/inbox.html', context)

@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=user)
    active_direct = None
    directs = None

    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=user, reciepient=message['user'])
        directs.update(is_read=True)

        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0

    last_login = user.last_login
    current_time = timezone.now()
    if current_time - last_login < timezone.timedelta(minutes=5):
        is_active = True
    else:
        is_active = False

    if request.user.username == active_direct:
        return redirect('/')
    
    if active_direct is None:
        # Return a different response or render a different template
        return render(request, 'autho/no_messages.html')
    else:
        sending_message_to = get_object_or_404(User, username=active_direct)
        offers = Offer.objects.filter(recipient=sending_message_to)
        user_offers = Offer.objects.filter(user=user)

    context = {
        'sending_message_to': sending_message_to,
        'directs': directs,
        'active_direct': active_direct,
        'messages': messages,
        'is_active': is_active,
        'offers': offers,
        'user_offers': user_offers,
    }
    return render(request, 'autho/inbox.html', context)

@login_required
def directs(request, username):
    sending_message_to = get_object_or_404(User, username=username)
    user = request.user
    messages = Message.get_message(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, reciepient__username=username)
    directs.update(is_read=True)

    last_login = user.last_login
    current_time = timezone.now()
    if current_time - last_login < timezone.timedelta(minutes=5):
        is_active = True
    else:
        is_active = False
    
    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0
        
    if request.user.username == username:
        return redirect('/')
    
    offers = Offer.objects.filter(recipient=sending_message_to)
    user_offers = Offer.objects.filter(user=request.user)

    context = {
        'sending_message_to': sending_message_to,
        'directs': directs,
        'active_direct': active_direct,
        'messages': messages,
        'is_active': is_active,
        'offers': offers,
        'user_offers': user_offers,
    }
    return render(request, 'autho/directs.html', context)

def send_message_ajax(request):
    if request.method == 'POST':
        from_user = request.user
        to_user_username = request.POST.get('to_user')
        body = request.POST.get('body')
        file = request.FILES.get('file')
        message_image = request.FILES.get('message_image')  
        offer_id = request.POST.get('offer')

        offer = None
        if offer_id:
            offer = Offer.objects.get(id=offer_id)

        to_user = User.objects.get(username=to_user_username)
        Message.send_message(from_user, to_user, body, offer, file, message_image)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failed'})

def get_messages_ajax(request, username):
    user = request.user
    sending_message_to = get_object_or_404(User, username=username)
    directs = Message.objects.filter(user=user, reciepient__username=username)
    directs.update(is_read=True)

    messages = []
    for direct in directs:
        message_data = {
            'sender': direct.sender.username,
            'body': direct.body,
            'date': direct.date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if direct.file:
            message_data['file_url'] = direct.file.url
        if direct.message_image:
            message_data['message_image_url'] = direct.message_image.url
        if direct.offer:  # Check if the offer attribute exists
            message_data['offer'] = {
                'pk': direct.offer.pk,
                'title': direct.offer.title,
                'price': direct.offer.price,
                'description': direct.offer.description,
                'created': direct.offer.created,
            }  # Add the offer's id, title, and price to the message_data
        messages.append(message_data)

    # print(messages)  # Add this line to print messages data
    return JsonResponse({'messages': messages})

def create_offer(request, username):
    offer_to = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.user = request.user
            offer.recipient = offer_to
            offer.save()
            return redirect('/')
    else:
        form = OfferForm()

    if request.user.username == username:
        return redirect('/')

    context = {
        'form': form,
        'offer_to': offer_to,
    }
    return render(request, 'autho/create_offer.html', context)

def display_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    context = {
        'offer': offer,
    }
    return render(request, 'autho/display_offer.html', context) 

@login_required
def delete_conversation(request, username):
    if request.method == 'POST':
        user = request.user
        other_user = get_object_or_404(User, username=username)

        # Delete messages in the conversation
        Message.objects.filter(
            (Q(sender=user) & Q(reciepient=other_user) & Q(user=user)) |
            (Q(sender=other_user) & Q(reciepient=user) & Q(user=user))
        ).delete()

        Message.objects.filter(
            (Q(sender=user) & Q(reciepient=other_user) & Q(user=other_user)) |
            (Q(sender=other_user) & Q(reciepient=user) & Q(user=other_user))
        ).delete()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failed'})

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_only(request):
    unique_conversations_list = Message.get_unique_conversations()
    paginator = Paginator(unique_conversations_list, 50)
    page_number = request.GET.get("page")
    unique_conversations = paginator.get_page(page_number)

    context = {
        'unique_conversations': unique_conversations,
    }
    return render(request, 'admin/admin_only.html', context)

@user_passes_test(is_admin)
def admin_only_search_user_convo(request):
    if request.method == 'POST':
        search_user = request.POST.get('search_user')
        convos = Message.get_unique_conversations_by_search(search_user)

        context = {
            'search_user': search_user,
            'convos': convos,
        }
        return render(request, 'admin/admin_only_search_user_convo.html', context)
    else:
        return render(request, 'admin/admin_only_search_user_convo.html')

@user_passes_test(is_admin)
def specific_user_conversation(request, username1, username2):
    user1 = User.objects.get(username=username1)
    user2 = User.objects.get(username=username2)

    conversation = Message.objects.filter(
        (Q(sender=user1) & Q(reciepient=user2)) | (Q(sender=user2) & Q(reciepient=user1))
    ).order_by('date')

    context = {
        'user1': user1,
        'user2': user2,
        'conversation': conversation,
    }
    return render(request, 'admin/specific_user_conversation.html', context)
