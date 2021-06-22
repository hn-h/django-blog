from django.shortcuts import render
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404,redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from blogApp.models import Post, Comment
from blogApp.forms import PostForm, CommentForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

class AboutView(TemplateView):
	template_name='blogApp/about.html'


class PostListView(ListView):
	model = Post

	def get_queryset(self):
		return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class PostDetailView(DetailView):
	model=Post


class PostCreateView(LoginRequiredMixin,CreateView):
	login_url = '/login/'
	redirect_field_name = 'blog/post_detail.html'
	model=Post
	form_class = PostForm


class PostUpdateView(LoginRequiredMixin,UpdateView):
	login_url='/login/'
	redirect_field_name = 'blog/post_detail.html'
	model=Post
	form_class = PostForm

class PostDeleteView(LoginRequiredMixin,DeleteView):
	model=Post
	success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin,ListView):
	login_url='/login/'
	redirect_field_name = 'blog/post_detail.html'
	model=Post
	template_name ='post_draft_list.html'

	def get_queryset(self):
		return Post.objects.filter(published_date__isnull=True).order_by('creation_date')


@login_required
def add_comment_to_post(request,pk):
	post=get_object_or_404(Post,pk=pk)
	if request.method=='POST':
		form=CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.save()
			return redirect('post_detail',pk=post.pk)

	else:
		form=CommentForm()
	return render(request,'blogApp/comment_form.html',{'form':form})

@login_required
def comment_approve(request,pk):
	comment=get_object_or_404(Comment,pk=pk)
	comment.approve()
	return redirect('post_detail',pk=comment.post.pk)

@login_required
def comment_remove(request,pk):
	comment=get_object_or_404(Comment,pk=pk)
	post_pk=comment.post.pk
	comment.delete()
	return redirect('post_detail',pk=post_pk)

@login_required
def post_publish(request,pk):
	post = get_object_or_404(Post,pk=pk)
	post.publish()
	return redirect('post_detail', pk=pk)

def signup(request):
	if request.method=="POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect('post_list')
	else:
		form = UserCreationForm()
	return render(request, 'registration/signup.html', {'form': form})
