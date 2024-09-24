from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'books'

urlpatterns = [
                  path('', HomeView.as_view(), name='home'),
                  path('search/', post_search, name='search'),
                  path('about-us/', AboutUsView.as_view(), name='about_us'),
                  path('books/', BookListView.as_view(), name='book_list'),
                  path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
                  path('tag/<slug:tag_slug>/',
                       BookListByTagView.as_view(), name='book_list_by_tag'),
                  path('authors/', AuthorListView.as_view(), name='author_list'),
                  path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),
                  path('view-pdf/<int:book_id>/', view_pdf, name='view_pdf'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
