from .models import Category

def menu_links(request):
    links = Category.objects.filter(is_deleted=False)
    return dict(links=links)

