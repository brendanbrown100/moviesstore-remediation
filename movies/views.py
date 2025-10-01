from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Petition, PetitionVote
from django.contrib.auth.decorators import login_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def petition(request):
    # Handle creating a new petition
    if request.method == 'POST':
        # Create petition
        if 'petition' in request.POST and request.POST['petition'].strip() != '':
            p = Petition()
            p.petition = request.POST['petition'].strip()
            p.user = request.user
            p.save()
            return redirect('movies.petition')

        # Handle voting: expect petition_id and choice in POST
        if 'petition_id' in request.POST and 'choice' in request.POST:
            try:
                petition_obj = Petition.objects.get(id=int(request.POST['petition_id']))
            except (ValueError, Petition.DoesNotExist):
                return redirect('movies.petition')

            choice_val = request.POST['choice']
            if choice_val not in ('0', '1'):
                return redirect('movies.petition')

            # Upsert vote for this user
            vote, created = PetitionVote.objects.get_or_create(
                petition=petition_obj,
                user=request.user,
                defaults={'choice': int(choice_val)}
            )
            if not created:
                vote.choice = int(choice_val)
                vote.save()

            return redirect('movies.petition')

    # GET: show petitions with vote counts and current user's vote
    petitions = Petition.objects.all().order_by('-date')
    petitions_data = []
    for p in petitions:
        yes_count = p.votes.filter(choice=1).count()
        no_count = p.votes.filter(choice=0).count()
        user_vote = None
        try:
            v = p.votes.get(user=request.user)
            user_vote = v.choice
        except PetitionVote.DoesNotExist:
            user_vote = None

        petitions_data.append({
            'petition': p,
            'yes': yes_count,
            'no': no_count,
            'user_vote': user_vote,
        })

    template_data = {}
    template_data['title'] = 'Petitions'
    template_data['petitions_data'] = petitions_data
    return render(request, 'movies/petition.html', {'template_data': template_data})