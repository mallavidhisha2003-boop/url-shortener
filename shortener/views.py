from django.shortcuts import redirect, render
from .models import URL
import random
import string
from django.shortcuts import render, redirect
from .models import URL
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
def generate_short_code(length=6):
    import random, string
    characters = string.ascii_letters + string.digits

    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        
        # Check if already exists in DB
        if not URL.objects.filter(short_code=code).exists():
            return code

def create_short_url(request):
    if request.method == 'POST':
        original_url = request.POST.get('url')
        custom_code = request.POST.get('custom_code')

        validator = URLValidator()

        try:
            validator(original_url)
        except ValidationError:
            return render(request, 'index.html', {'error': 'Invalid URL'})

        # 👉 FIXED INDENTATION HERE
        if custom_code:
            if URL.objects.filter(short_code=custom_code).exists():
                return render(request, 'index.html', {'error': 'Custom code already taken'})
            short_code = custom_code
        else:
            short_code = generate_short_code()

        URL.objects.create(
            original_url=original_url,
            short_code=short_code
        )

        short_url = request.build_absolute_uri(short_code)

        return render(request, 'index.html', {'short_url': short_url})

    return render(request, 'index.html')
from django.core.cache import cache

def redirect_url(request, code):
    # Step 1: check cache first
    url = cache.get(code)

    if url:
        url.clicks += 1
        url.save()
        return redirect(url.original_url)

    try:
        url = URL.objects.get(short_code=code)

        # Step 2: store in cache
        cache.set(code, url, timeout=60*5)  # 5 minutes

        url.clicks += 1
        url.save()

        return redirect(url.original_url)

    except URL.DoesNotExist:
        return render(request, '404.html')

def stats_view(request):
    urls = URL.objects.all().order_by('-created_at')
    return render(request, 'stats.html', {'urls': urls}) 