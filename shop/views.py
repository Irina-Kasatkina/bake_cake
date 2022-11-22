from django.shortcuts import render


def index(request):
    # places = Place.objects.all()

    context = {
    }
    return render(request, 'index.html', context)
