from django.shortcuts import render,redirect

from books.models import Book,Fav
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile

from books.owner import OwnerListView, OwnerDetailView,OwnerDeleteView
from django.urls import reverse
from books.forms import CreateForm
from books.forms import CommentForm
from books.models import Comment

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

from books.utils import dump_queries
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import naturaltime

#
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from books.forms import SignUpForm
# Create your views here.
from django.contrib import messages

class BookListView(OwnerListView):
    model = Book
    # By convention:
    # template_name = "myarts/article_list.html"
    template_name = "books/book_list.html"
    #
    def get(self, request) :
        book_list = Book.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_books.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        #weeeeeeeeellllllllllllllll
        strval =  request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # objects = Ad.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            query = Q(name__contains=strval)
            query.add(Q(condition__contains=strval), Q.OR)
            objects = Book.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            # try both versions with > 4 Ads and watch the queries that happen
            objects = Book.objects.all().order_by('-updated_at')[:10]

            # objects = Ad.objects.select_related().all().order_by('-updated_at')[:10]

        # Augment the Ad_list
        for obj in objects:
            obj.natural_updated = naturaltime(obj.updated_at)
        #weeeeeeelllllllllllll(chech here)
        ctx = {'book_list' : objects, 'favorites': favorites,'search': strval}
        retval = render(request, self.template_name, ctx)
        dump_queries()
        return retval;
    #


class BookDetailView(OwnerDetailView):
    model = Book
    template_name = "books/book_detail.html"
    def get(self, request, pk) :
        x = Book.objects.get(id=pk)
        comments = Comment.objects.filter(book=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = { 'book' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)


class BookCreateView(LoginRequiredMixin, View):
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)


class BookUpdateView(LoginRequiredMixin, View):
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:all')

    def get(self, request, pk):
        pic = get_object_or_404(Book, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        pic = get_object_or_404(Book, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        pic = form.save(commit=False)
        pic.save()

        return redirect(self.success_url)


class BookDeleteView(OwnerDeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Book, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, book=f)
        comment.save()
        return redirect(reverse('books:book_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "books/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        book = self.object.book
        return reverse('books:book_detail', args=[book.id])

def stream_file(request, pk):
    pic = get_object_or_404(Book, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.image)
    response.write(pic.image)
    return response

#=================================================================
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Account created Succesfully Welcome!')
            return redirect('/books')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
#=================================================================

#for favorite:

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Book, id=pk)
        fav = Fav(user=request.user, book=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

class BookFavView(OwnerListView):
    model = Book
    template_name = "books/book_favorite.html"
    #=========================================

    def get(self, request) :
        book_list = Book.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_books.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        #weeeeeeeeellllllllllllllll
        strval =  request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # objects = Ad.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            query = Q(name__contains=strval)
            query.add(Q(condition__contains=strval), Q.OR)
            objects = Book.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            # try both versions with > 4 Ads and watch the queries that happen
            objects = Book.objects.all().order_by('-updated_at')[:10]

            # objects = Ad.objects.select_related().all().order_by('-updated_at')[:10]

        # Augment the Ad_list
        for obj in objects:
            obj.natural_updated = naturaltime(obj.updated_at)
        #weeeeeeelllllllllllll(chech here)
        ctx = {'book_list' : objects, 'favorites': favorites,'search': strval}
        retval = render(request, self.template_name, ctx)
        dump_queries()
        return retval

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Book, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, book=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()