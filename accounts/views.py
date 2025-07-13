from django.shortcuts import render,redirect
from .models import Account
from .forms import RegistrationForm
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages, auth
from carts.models import Cart,CartItem
from carts.views import __cart_id
# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # confirm_password = form.cleaned_data['confirm_password']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name = first_name,last_name= last_name,email = email,username = username,password= password)
            user.phone_number = phone_number
            user.save()
            # user activation link 
            current_site = get_current_site(request)
            mail_subject = "Please Activate Your Account"
            message = render_to_string('accounts/activation.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            # messages.success(request, "Thank you for registering with us. Please Check your mail for verification")
            url = reverse('login')  # Make sure 'login' is the name of the login view in your urls.py
        return redirect(f"{url}?command=verification&email={email}")
    else:
        form = RegistrationForm()
    context = {
        'form' : form,
    }
    return render(request,"accounts/register.html",context=context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                print("Entering into try block")
                cart = Cart.objects.get(cart_id=__cart_id(request))
                cart_item_qs = CartItem.objects.filter(cart=cart)

                if cart_item_qs.exists():
                    product_variation = [] 
                    for item in cart_item_qs:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    cart_items = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id_list = []

                    for item in cart_items:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id_list.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id_list[index]
                            existing_item = CartItem.objects.get(id=item_id)
                            existing_item.quantity += 1
                            existing_item.user = user
                            existing_item.save()
                        else:
                            for item in cart_item_qs:
                                item.user = user
                                item.save()
            except Exception as e:
                print(f"Error merging cart: {str(e)}")

            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, "accounts/login.html")

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,"You Logged Out succesfully")
    return  redirect("login")


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,OverflowError,ValueError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,"Congratulations..!! Your Account is Activated")
        return redirect('login')
    else:
        messages.error(request,"Invalid Activation Link")
        return redirect('register')

@login_required(login_url = 'login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user =  Account.objects.get(email__exact=email)
            # USER ACTIVATION 
            current_site = get_current_site(request)
            mail_subject = "Reset Your Link"
            message = render_to_string('accounts/reset_password_validate.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            
            messages.success(request,"Password Reset mail has been sent to your email Account")
            return redirect('login')
        else:
            messages.error(request,"Account does not exist")
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,OverflowError,ValueError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,"Please Reset your password")
        return redirect('resetPassword')
    else:
        messages.error(request,"This link have been expired")
        return redirect('login')
    
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successfull")
            return redirect(('login'))
        else:
            messages.error(request,"Passwords do not match")
            return redirect('resetPassword')
    else:
        return render(request,'accounts/reset_password.html')
