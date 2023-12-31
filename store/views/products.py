import json
from django.shortcuts import render, redirect
from django.views import View
from store.models.products import Products
from store.models.category import Category
from store.models.user import CustomUser
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.middleware.csrf import rotate_token
from django.views.decorators.csrf import csrf_protect
import re
import bleach
from django.contrib import messages

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'customer' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            next_url = request.get_full_path()
            return redirect(f'/login?next={next_url}')
    return wrapper

def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'customer' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            next_url = request.get_full_path()
            return redirect(f'/login?next={next_url}')
    return wrapper

@method_decorator(csrf_protect, name='dispatch')
class ProductView(View): 
    def get(self, request, product_id):
        product = Products.objects.get(id=product_id)
        review = json.loads(product.review)
        return render(request, 'products.html', {'product' : product, 'reviews': review})
    
    

    @method_decorator(custom_login_required)
    def post(self, request, product_id):
        rotate_token(request)
        product_name = request.POST.get('product')
        customer_id = request.POST.get('customer')
        review_text = request.POST.get('review')
        review_text=''.join(review_text)
        x=re.search("<script(.*)script>",review_text)
        y=re.search("alert(.*)\)", review_text)
        z=re.search("javascript:", review_text)
        if x or y or z:
            messages.info(request, 'Invalid Input')
            return redirect(f'/product/{product_id}')
        else:
            sani_review= bleach.clean(review_text)
            print(sani_review)
            review_text=sani_review
            customer = CustomUser.objects.get(id=customer_id)
            customer_name = customer.first_name + " " + customer.last_name
            product_db = Products.objects.get(id=product_id)
            new_review = {"customer_name": customer_name, "review": review_text}

            if product_db.review == '{}':
            # If there are no existing reviews, create a new list with the new review
                reviews = [new_review]
            else:
            # If there are existing reviews, append the new review to the list
                reviews = json.loads(product_db.review)
                reviews.append(new_review)

        # Convert the list of reviews back to a string and update the product in the database
            Products.objects.filter(id=product_id).update(review=json.dumps(reviews))

            return redirect(f'/product/{product_id}')




