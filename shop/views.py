from random import randint
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import login,logout
from django.contrib import messages
from .models import Category, Product
from .forms import LoginForm, RegistrationForm



class Index(ListView):
    """Главная страница"""
    model = Product
    context_object_name = 'categories'
    extra_context = {'title': 'Главная страница'}
    template_name = 'shop/index.html'

    def get_queryset(self):
        """Вывод родительской категории"""
        categories = Category.objects.filter(parent=None)
        return categories
    
    def get_context_data(self, **kwargs):
        """Вывод на страницу дополнительных элементов"""
        context = super().get_context_data()
        context['top_products'] = Product.objects.order_by('-watched')[:8]
        return context
        
    
class Subcategories(ListView):
    """Вывод подкатегорий на отдельной странице"""
    model = Product
    context_object_name = 'products'
    template_name = 'shop/category_page.html'

    def get_queryset(self):
        """Получение всех товаров подкатегории"""
        type_field = self.request.GET.get('type')
        if type_field:
            products = Product.objects.filter(category__slug = type_field)
            return products

        parent_category = Category.objects.get(slug=self.kwargs['slug'])
        subcategories = parent_category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories).order_by('?')
        
        if sort_field := self.request.GET.get('sort'):
            products = products.order_by(sort_field)

        return products
    

    def get_context_data(self, **kwargs):
        """Дополнительные элементы"""
        context = super().get_context_data()
        parent_category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = parent_category 
        context['title'] = parent_category.title
        return context


class ProductPage(DetailView):
    """Вывод товара на отдельной странице"""
    model = Product
    context_object_name = 'product'
    template_name = 'shop/product_page.html'
    

    def get_context_data(self, **kwargs):
        """Вывод на страничку дополнтельных элементов """
        context = super().get_context_data()
        product = Product.objects.get(slug= self.kwargs['slug'])
        context['title']= product.title
        # products = Product.objects.filter(category= product.category)
       

        # data = []
        
        # for i in range(5):
        #     random_index = randint(0, len(products) - 1)
        #     random_product = products[random_index]
        #     if random_product not in data and str(random_product) != product.title:
        #         data.append(random_product)
        
        # context['products']= data

        data = Product.objects.all().exclude(slug= self.kwargs['slug']).filter(category = product.category)[:5]
        context['products']= data


        return context
    


def login_registration(request):
    context = {'title': 'Войти или зарегистрироваться',
               'login_form': LoginForm,
               'registration_form': RegistrationForm}

    return render(request, 'shop/login_registration.html', context)




def user_login(request):
    """Войти"""
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('index')
    else:
        messages.error(request, 'Неверное имя пользователя или пароль')
        return redirect('login_registration')

def user_logout(request):
    """Выйти"""
    logout(request)
    return redirect('index')



def user_registration(request):
    """Регистрация"""
    form = RegistrationForm(data= request.POST)
    if form.is_valid():
        form.save()
        messages.success(request,"Аккаунт успешно создан")
    else:
        for error in form.errors:
             messages.error(request, form.errors[error].as_text())
        # messages.error(request, 'Что-то пошло не так')

    return redirect('login_registration')
