from django.urls import path, reverse_lazy
from . import views

#===========================================================================

#===========================================================================
app_name='books'
urlpatterns = [
    path('', views.BookListView.as_view(),name='all'),   #for home page rendering
   #path('books', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book_detail'),
    path('book/create',
        views.BookCreateView.as_view(success_url=reverse_lazy('books:all')), name='book_create'),
    path('book/<int:pk>/update',
        views.BookUpdateView.as_view(success_url=reverse_lazy('books:all')), name='book_update'),
    path('book/<int:pk>/delete',
        views.BookDeleteView.as_view(success_url=reverse_lazy('books:all')), name='book_delete'),
    path('book_image/<int:pk>', views.stream_file, name='book_image'),
    path('book/<int:pk>/comment',
        views.CommentCreateView.as_view(), name='book_comment_create'),
    path('comment/<int:pk>/delete',
        views.CommentDeleteView.as_view(success_url=reverse_lazy('books')), name='book_comment_delete'),
    path('book/<int:pk>/favorite',
    views.AddFavoriteView.as_view(), name='book_favorite'),
    path('book/<int:pk>/unfavorite',
    views.DeleteFavoriteView.as_view(), name='book_unfavorite'),
    #================================================================
    path('fav', views.BookFavView.as_view(),name='fav'),
]