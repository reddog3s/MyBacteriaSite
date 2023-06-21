from django.shortcuts import  render, redirect, get_object_or_404
from .forms import NewUserForm, NewMicrobeFrom, NewPostFrom, PostFilter, MicrobeFilter, CSV_form
from MyBacteriaSite.models import MicrobePost, Microbe
from django.contrib.auth.models import User
from django.db.models import Count,Avg, Max, Min, Sum
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.urls import reverse
import csv
import io
from io import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from datetime import datetime
from django.http import JsonResponse


def homepage(request):

    context = {
        'posts': list(MicrobePost.objects.values('latitude', 'longitude'))
    }

    return render(request, 'homepage.html', context)

def posts_positions(request):
    return JsonResponse({
        'posts': list(MicrobePost.objects.values('latitude', 'longitude'))
    })


def gallery(request):
    posts = MicrobePost.objects.all().order_by('created_date')
    posts = posts.annotate(num_of_likes=Count('likes'))

    search_form = PostFilter(request.GET)
    if search_form.is_valid():
        cd = search_form.cleaned_data
        if cd['author']:
            users = User.objects.filter(username__icontains=cd['author'])
            posts = posts.filter(author_id__in=users)
        if cd['title']:
            posts = posts.filter(title__icontains=cd['title'])
        if cd['microbe']:
            microbes = Microbe.objects.filter(MicrobeSpecies__icontains=cd['microbe'])
            posts = posts.filter(microbe_id__in=microbes)
        if cd['created_date_high_th']:
            posts = posts.filter(created_date__gte=cd['created_date_high_th'])
        if cd['created_date_low_th']:
            posts = posts.filter(created_date__lte=cd['created_date_low_th'])
        if cd['num_of_likes_high_th']:
            #posts = posts.alias(num_of_likes=Count('likes')).filter(num_of_likes__gte=cd['num_of_likes_high_th'])  
            posts = posts.filter(num_of_likes__gte=cd['num_of_likes_high_th'])
        if cd['num_of_likes_low_th']:
            #posts = posts.alias(num_of_likes=Count('likes')).filter(num_of_likes__lte=cd['num_of_likes_low_th'])
            posts = posts.filter(num_of_likes__lte=cd['num_of_likes_low_th'])
        



    p = Paginator(posts, 6)
    page = request.GET.get('page', 1)
    posts = p.get_page(page)

    context = {'posts' : posts, 'search_form' : search_form}   
    return render(request, 'gallery.html', context)

def report_pdf(request):
    # create bytestream buffer
    buf = io.BytesIO()

    # create canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)

    # create text obj
    textobj = c.beginText()
    textobj.setTextOrigin(inch, inch)
    textobj.setFont("Helvetica", 14)


    # queries
    microbes = Microbe.objects.annotate(num_of_posts=Count('microbepost'))
    posts = MicrobePost.objects.annotate(num_of_likes=Count('likes'))

    # get current date
    now = datetime.now()
    current_month = now.month
    current_year = now.year


    header = "MyBacteriaSite report"
    report_date = "Report generated: " + now.strftime("%m.%d.%Y, %H:%M:%S")
    lines = [header, report_date, " " , " "]

    # all posts number
    number_of_posts = posts.count()
    number_of_posts = "Total number of posts: " + str(number_of_posts)
    lines.append(number_of_posts)
    lines.append(" ")


    # posts added this month
    temp = posts.filter(created_date__year=current_year)
    temp = temp.filter(created_date__month=current_month)

    posts_this_month = temp.count()
    posts_this_month = "Number of posts this month: " + str(posts_this_month)
    lines.append(posts_this_month)
    lines.append(" ")
    
    # most liked post
    max_likes = posts.aggregate(Max('num_of_likes'))
    max_likes = max_likes['num_of_likes__max']
    most_liked_posts = posts.filter(num_of_likes__gte = max_likes)

    # check if it's only one post
    if isinstance(most_liked_posts, MicrobePost):
        most_liked_posts = [most_liked_posts]

    lines.append("Most liked post of all time")
    lines.append(" ")
    for post in most_liked_posts:
        lines.append("Author: " + post.author.username)
        lines.append("Title: " + post.title)
        lines.append("Number of likes: " + str(post.number_of_likes()))
        lines.append(" ")



    # most liked post this month
    max_likes_this_month = temp.aggregate(Max('num_of_likes'))
    max_likes_this_month = max_likes_this_month['num_of_likes__max']
    most_liked_posts_this_month = posts.filter(num_of_likes__gte = max_likes_this_month)

    # check if it's only one post
    if isinstance(posts, MicrobePost):
        posts = [posts]

    lines.append("Most liked post this month")
    lines.append(" ")
    for post in most_liked_posts_this_month:
        lines.append("Author: " + post.author.username)
        lines.append("Title: " + post.title)
        lines.append("Number of likes: " + str(post.number_of_likes()))
        lines.append(" ")


    # microbe with most posts
    most_posts_microbe = microbes.aggregate(Max('num_of_posts'))
    most_posts_microbe = most_posts_microbe['num_of_posts__max']
    microbe_most_posts = microbes.filter(num_of_posts__gte = most_posts_microbe)

    # check if it's only one post
    if isinstance(microbe_most_posts, MicrobePost):
        microbe_most_posts = [microbe_most_posts]
    

    lines.append("Microbe with most posts")
    lines.append(" ")

    for microbe in microbe_most_posts:
        lines.append("Microbe: " + microbe.MicrobeSpecies)
        lines.append("Number of posts: " + str(microbe.num_of_posts))
        lines.append(" ")




    # add lines of text
    for line in lines:
        textobj.textLine(line)

    
    # Finish
    c.drawText(textobj)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='report.pdf')




def microbe_list(request):
    microbes = Microbe.objects.all().order_by('MicrobePhylum')
    microbes = microbes.annotate(num_of_posts=Count('microbepost'))



    search_microbe_form = MicrobeFilter(request.GET)
    if search_microbe_form.is_valid():
        cd = search_microbe_form.cleaned_data
        if cd['Phylum']:
            microbes = microbes.filter(MicrobePhylum__icontains=cd['Phylum'])
        if cd['Class']:
            microbes = microbes.filter(MicrobeClass__icontains=cd['Class'])
        if cd['Order']:
            microbes = microbes.filter(MicrobeOrder__icontains=cd['Order'])
        if cd['Family']:
            microbes = microbes.filter(MicrobeFamily__icontains=cd['Family'])
        if cd['Genus']:
            microbes = microbes.filter(MicrobeGenus__icontains=cd['Genus'])
        if cd['Species']:
            microbes = microbes.filter(MicrobeSpecies__icontains=cd['Species'])
        if cd['num_of_posts_high_th']:
            microbes = microbes.filter(num_of_posts__gte=cd['num_of_posts_high_th'])
        if cd['num_of_posts_low_th']:
            microbes = microbes.filter(num_of_posts__lte=cd['num_of_posts_low_th'])

        



    p = Paginator(microbes, 10)
    page = request.GET.get('page', 1) 
    microbes = p.get_page(page)

    context = {'microbes' : microbes, 'search_microbe_form' : search_microbe_form}   
    return render(request, 'microbe_list.html', context)

def delete_microbe(request, pk):
    microbe = Microbe.objects.get(id=pk)

    if request.user.is_superuser:
        microbe.delete()
        messages.info(request, "You have deleted a microbe")
    else:
        messages.error(request, "You have to be an admin to delete microbes")
        return redirect("MyBacteriaSite:microbe_list")

    return redirect("MyBacteriaSite:microbe_list")


def edit_microbe(request, pk):
    microbe = Microbe.objects.get(id=pk)

    context={}
    if request.user.is_superuser:
        if request.method == "POST":
            form = NewMicrobeFrom(request.POST, instance = microbe)
            if form.is_valid():
                microbe = form.save(commit = False)

                microbe.save()
                print('Success')
                messages.success(request, 'Microbe edited successfully')

                return redirect("MyBacteriaSite:microbe_list")
            else:
                errors = form.errors 
                non_field = form.non_field_errors()
                context.update({"form_errors":errors})
                context.update({"non_field_errors":non_field})
                print('Error\n')
                messages.error(request, "Invalid microbe information")
                #messages.error(request, errors)
        else:
            form = NewMicrobeFrom(instance = microbe)
    else:
        messages.error(request, "You have to be an admin to edit microbes")
        return redirect("MyBacteriaSite:microbe_list")
	
    
    context.update({"microbe_form":form})

    return render(request, 'edit_microbe.html', context)


def add_microbe(request):

    context={}
    if request.user.is_superuser:
        if request.method == "POST":
            form = NewMicrobeFrom(request.POST)
            if form.is_valid():

                form.save()
                print('Success')
                messages.success(request, 'New microbe added successfully')

                return redirect("MyBacteriaSite:microbe_list")
            else:
                errors = form.errors 
                non_field = form.non_field_errors()
                context.update({"form_errors":errors})
                context.update({"non_field_errors":non_field})
                print('Error\n')
                messages.error(request, "Invalid post information")
                #messages.error(request, errors)
        else:
            form = NewMicrobeFrom()
    else:
        messages.error(request, "You have to be an admin to add microbes")
	
    
    context.update({"microbe_form":form})

    return render(request, 'add_microbe.html', context)


def microbes_as_csv(request):

    context={}
    if request.user.is_superuser:
        if request.method == "POST":
            form = CSV_form(request.POST, request.FILES)
            if form.is_valid():

                file = request.FILES.get("csv_file")

                # decode to string
                output = " "
                for chunk in file.chunks():
                    output += chunk.decode('utf-8')

                # convert a string to a file object 
                # we need to decode it from file-like object to string and then again make it file-like object
                f = StringIO(output)
                reader = csv.reader(f)
                next(reader)  # Advance past the header
                for row in reader:
                     print(row)
                     _, created = Microbe.objects.get_or_create(
                        MicrobePhylum = row[0],
                        MicrobeClass = row[1],
                        MicrobeOrder = row[2],
                        MicrobeFamily = row[3],
                        MicrobeGenus = row[4],
                        MicrobeSpecies = row[5],
                        description = row[6])

                    
                print('Success')
                messages.success(request, 'New microbes added successfully')

                return redirect("MyBacteriaSite:microbe_list")
            else:
                errors = form.errors 
                non_field = form.non_field_errors()
                context.update({"form_errors":errors})
                context.update({"non_field_errors":non_field})
                print('Error\n')
                messages.error(request, "Invalid post information")
                #messages.error(request, errors)
        else:
            form = CSV_form()
    else:
        messages.error(request, "You have to be an admin to add microbes")
	
    form = CSV_form()
    context.update({"CSV_form":form})

    return render(request, 'microbe_as_csv.html', context)




def show_post(request, pk):
    post = MicrobePost.objects.get(id=pk)
    number_of_likes = post.number_of_likes()

    liked = False
    if post.likes.filter(id=request.user.id).exists():
        liked = True

    context = {'post' : post, 'number_of_likes' : number_of_likes, 'post_is_liked' : liked}   
    return render(request, 'show_post.html', context)


def like_post(request, pk):
    post = get_object_or_404(MicrobePost, id=request.POST.get('post_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('MyBacteriaSite:show_post', args=[str(pk)]))


def delete_post(request, pk):
    post = MicrobePost.objects.get(id=pk)

    if request.user.is_authenticated and request.user == post.author:
        if post.image:
            post.image.delete()
        post.delete()
        messages.info(request, "You have deleted your post")
    else:
        messages.error(request, "You have to be logged in and be a posts' author to delete posts")
        return redirect("MyBacteriaSite:homepage")

    return redirect("MyBacteriaSite:profile")


def edit_post(request, pk):
    post = MicrobePost.objects.get(id=pk)

    context={}
    if request.user.is_authenticated and request.user == post.author:
        if request.method == "POST":
            form = NewPostFrom(request.POST, request.FILES, instance = post)
            if form.is_valid():

                post = form.save(commit = False)

                post.save()
                print('Success')
                messages.success(request, 'Post edited successfully')

                return redirect("MyBacteriaSite:profile")
            else:
                errors = form.errors 
                non_field = form.non_field_errors()
                context.update({"form_errors":errors})
                context.update({"non_field_errors":non_field})
                print('Error\n')
                messages.error(request, "Invalid post information")
                #messages.error(request, errors)
        else:
            form = NewPostFrom(instance = post)
    else:
        messages.error(request, "You have to be logged in and be post author to edit posts")
        return redirect("MyBacteriaSite:homepage")
	
    context.update({"post_form":form})

    return render(request, 'edit_post.html', context)

def add_post(request):
    context={}
    if request.user.is_authenticated:
        if request.method == "POST":
            form = NewPostFrom(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit = False)
                # get author
                post.author = request.user

                post.save()
                print('Success')
                messages.success(request, 'Post published successfully')

                return redirect("MyBacteriaSite:profile")
            else:
                errors = form.errors 
                non_field = form.non_field_errors()
                context.update({"form_errors":errors})
                context.update({"non_field_errors":non_field})
                print('Error\n')
                messages.error(request, "Invalid post information")
        else:
            form = NewPostFrom()
    else:
        messages.error(request, "You have to be logged in to publish posts")
	
    
    context.update({"post_form":form})
	
    return render(request, 'add_post.html', context=context)




def profile(request):
    context = {}
    if request.user.is_authenticated:
        total_number_of_posts = MicrobePost.objects.filter(author_id__exact=request.user.id).count()
        context.update({'total_number_of_posts' : total_number_of_posts})
        try:
            posts = MicrobePost.objects.filter(author_id__exact=request.user.id).order_by('created_date')
            posts = posts.annotate(num_of_likes=Count('likes'))
            # if it isn't iterable (it's single object), make it list
            if isinstance(posts, MicrobePost):
                posts = [posts]
            
            p = Paginator(posts, 6)
            page = request.GET.get('page', 1)
            posts = p.get_page(page)
            context.update({'posts' : posts})
        except:
            posts = None
            context.update({'posts' : posts})
    else:
        messages.error(request, "You have to be logged in to access profile")
        return redirect("MyBacteriaSite:homepage")

    return render(request, 'profile.html', context)


def edit_profile(request):
    context={}
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if request.method == "POST":
            form = NewUserForm(request.POST, instance = current_user)
            if form.is_valid():
                user = form.save()
                user.refresh_from_db()
                user.profile.birthdate = form.cleaned_data.get('birthdate')
                user.profile.country = form.cleaned_data.get('country')
                user.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)

                print('Success')
                messages.success(request, 'Account information edited successfully')

                return redirect("MyBacteriaSite:profile")
            else:
                errors = form.errors 
                non_field = form.non_field_errors()
                context.update({"form_errors":errors})
                context.update({"non_field_errors":non_field})
                print('Error\n')
                messages.error(request, "Unsuccessful edit. Invalid information.")
                #messages.error(request, errors)
        else:
            form = NewUserForm(instance = current_user)
    else:
        messages.error(request, "You have to be logged in to access profile")
        return redirect("MyBacteriaSite:homepage")
	

    context.update({"register_form":form})
    return render(request=request, template_name="edit_profile.html", context=context)   


def register_request(request):
    context={}
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.birthdate = form.cleaned_data.get('birthdate')
            user.profile.country = form.cleaned_data.get('country')
            user.save()
            # username = form.cleaned_data.get('username')
            # password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=password)

            print('Success')
            messages.success(request, 'Account created successfully')

            return redirect("MyBacteriaSite:homepage")
        else:
            errors = form.errors 
            non_field = form.non_field_errors()
            context.update({"form_errors":errors})
            context.update({"non_field_errors":non_field})
            print('Error\n')
            messages.error(request, "Unsuccessful registration. Invalid information.")
            #messages.error(request, errors)
    else:
        form = NewUserForm()
    
    context.update({"register_form":form})
    return render(request=request, template_name="register.html", context=context)



def login_request(request):
    context={}
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("MyBacteriaSite:homepage")
            else:
                errors = form.errors
                non_field = form.non_field_errors()
                context.update({"form_errors":errors})
                context.update({"non_field_errors":non_field})
                messages.error(request,"Invalid username or password.")
        else:
            errors = form.errors
            non_field = form.non_field_errors()
            context.update({"form_errors":errors})
            context.update({"non_field_errors":non_field})
            messages.error(request,"Invalid username or password.")
    else:
        form = AuthenticationForm()

    context.update({"login_form":form})
    return render(request=request, template_name="login.html", context=context)

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("MyBacteriaSite:homepage")

