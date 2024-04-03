from django.urls import path, reverse_lazy
from . import views

#===========================================================================

#===========================================================================
app_name='payingguest'
urlpatterns = [
    path('', views.PayingguestListView.as_view(),name='all'),   #for home page rendering
   #path('payingguests', views.PayingguestListView.as_view(), name='payingguests'),
    path('payingguest/<int:pk>', views.PayingguestDetailView.as_view(), name='payingguest_detail'),
    path('payingguest/create',
        views.PayingguestCreateView.as_view(success_url=reverse_lazy('payingguest:all')), name='payingguest_create'),
    path('payingguest/<int:pk>/update',
        views.PayingguestUpdateView.as_view(success_url=reverse_lazy('payingguest:all')), name='payingguest_update'),
    path('payingguest/<int:pk>/delete',
        views.PayingguestDeleteView.as_view(success_url=reverse_lazy('payingguest:all')), name='payingguest_delete'),
    path('payingguest_image/<int:pk>', views.stream_file, name='payingguest_image'),
    path('payingguest/<int:pk>/comment',
        views.CommentCreateView.as_view(), name='payingguest_comment_create'),
    path('comment/<int:pk>/delete',
        views.CommentDeleteView.as_view(success_url=reverse_lazy('payingguest_detail')), name='payingguest_comment_delete'),
    path('payingguest/<int:pk>/favorite',
    views.AddFavoriteView.as_view(), name='payingguest_favorite'),
    path('payingguest/<int:pk>/unfavorite',
    views.DeleteFavoriteView.as_view(), name='payingguest_unfavorite'),
    #================================================================
    path('fav', views.PayingguestFavView.as_view(),name='fav'),
]