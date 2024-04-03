from django.shortcuts import render,redirect

from payingguest.models import Payingguest,PGFav
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile

from payingguest.owner import OwnerListView, OwnerDetailView,OwnerDeleteView
from django.urls import reverse
from payingguest.forms import PGCreateForm
from payingguest.forms import PGCommentForm
from payingguest.models import PGComment

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

from payingguest.utils import dump_queries
from django.db.models import Q
from django.contrib.humanize.templatetags.humanize import naturaltime

#
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from payingguest.forms import PGSignUpForm
# Create your views here.
from django.contrib import messages

class PayingguestListView(OwnerListView):
    model = Payingguest
    # By convention:
    # template_name = "myarts/article_list.html"
    template_name = "payingguest/payingguest_list.html"
    #
    def get(self, request) :
        payingguest_list = Payingguest.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_payingguest.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        #weeeeeeeeellllllllllllllll
        strval =  request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # objects = Ad.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            query = Q(City__contains=strval)
            query.add(Q(condition__contains=strval), Q.OR)
            objects = Payingguest.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            # try both versions with > 4 Ads and watch the queries that happen
            objects = Payingguest.objects.all().order_by('-updated_at')[:10]

            # objects = Ad.objects.select_related().all().order_by('-updated_at')[:10]

        # Augment the Ad_list
        for obj in objects:
            obj.natural_updated = naturaltime(obj.updated_at)
        #weeeeeeelllllllllllll(chech here)
        ctx = {'payingguest_list' : objects, 'favorites': favorites,'search': strval}
        retval = render(request, self.template_name, ctx)
        dump_queries()
        return retval;
    #


class PayingguestDetailView(OwnerDetailView):
    model = Payingguest
    template_name = "payingguest/payingguest_detail.html"
    def get(self, request, pk) :
        x = Payingguest.objects.get(id=pk)
        comments = PGComment.objects.filter(payingguest=x).order_by('-updated_at')
        comment_form = PGCommentForm()
        context = { 'payingguest' : x, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context)


class PayingguestCreateView(LoginRequiredMixin, View):
    template_name = 'payingguest/payingguest_form.html'
    success_url = reverse_lazy('payingguest:all')

    def get(self, request, pk=None):
        form = PGCreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = PGCreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()
        return redirect(self.success_url)


class PayingguestUpdateView(LoginRequiredMixin, View):
    template_name = 'payingguest/payingguest_form.html'
    success_url = reverse_lazy('payingguest:all')

    def get(self, request, pk):
        pic = get_object_or_404(Payingguest, id=pk, owner=self.request.user)
        form = PGCreateForm(instance=pic)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        pic = get_object_or_404(Payingguest, id=pk, owner=self.request.user)
        form = PGCreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        pic = form.save(commit=False)
        pic.save()

        return redirect(self.success_url)


class PayingguestDeleteView(OwnerDeleteView):
    model = Payingguest
    template_name = "payingguest/payingguest_confirm_delete.html"

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Payingguest, id=pk)
        comment = PGComment(text=request.POST['comment'], owner=request.user, payingguest=f)
        comment.save()
        return redirect(reverse('payingguest:payingguest_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = PGComment
    template_name = "payingguest/payingguest_comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        payingguest = self.object.payingguest
        return reverse('payingguest:payingguest_detail', args=[payingguest.id])

def stream_file(request, pk):
    pic = get_object_or_404(Payingguest, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.image)
    response.write(pic.image)
    return response

#=================================================================
def signup(request):
    if request.method == 'POST':
        form = PGSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Account created Succesfully Welcome!')
            return redirect('/payingguest')
    else:
        form = PGSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
#=================================================================

#for favorite:

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        t = get_object_or_404(Payingguest, id=pk)
        fav = PGFav(user=request.user, payingguest=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

class PayingguestFavView(OwnerListView):
    model = Payingguest
    template_name = "payingguest/payingguest_favorite.html"
    #=========================================

    def get(self, request) :
        payingguest_list = Payingguest.objects.all()
        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_payingguest.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]
        #weeeeeeeeellllllllllllllll
        strval =  request.GET.get("search", False)
        if strval :
            # Simple title-only search
            # objects = Ad.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            query = Q(City__contains=strval)
            query.add(Q(condition__contains=strval), Q.OR)
            objects = Payingguest.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            # try both versions with > 4 Ads and watch the queries that happen
            objects = Payingguest.objects.all().order_by('-updated_at')[:10]

            # objects = Ad.objects.select_related().all().order_by('-updated_at')[:10]

        # Augment the Ad_list
        for obj in objects:
            obj.natural_updated = naturaltime(obj.updated_at)
        #weeeeeeelllllllllllll(chech here)
        ctx = {'payingguest_list' : objects, 'favorites': favorites,'search': strval}
        retval = render(request, self.template_name, ctx)
        dump_queries()
        return retval

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        t = get_object_or_404(Payingguest, id=pk)
        try:
            fav = PGFav.objects.get(user=request.user, payingguest=t).delete()
        except PGFav.DoesNotExist as e:
            pass

        return HttpResponse()