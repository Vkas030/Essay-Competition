from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import UserTask
from .utils import evaluate_essay  # <- updated import

# --------------------------------------
# Submit Essay View
# --------------------------------------
@login_required
def submit_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            essay = form.cleaned_data["essay_text"]

            # Evaluate essay using spelling + grammar
            score = evaluate_essay(essay)

            # Save task in database
            UserTask.objects.create(
                user=request.user,
                essay_text=essay,
                score=score
            )

            return redirect("tasks:ranking")

    else:
        form = TaskForm()

    return render(request, "submit_task.html", {"form": form})


# --------------------------------------
# Ranking / Leaderboard View
# --------------------------------------
@login_required
def ranking(request):
    # Sort by highest score first, then earliest submission
    rankings = UserTask.objects.order_by("-score", "submitted_at")
    return render(request, "ranking.html", {"rankings": rankings})


# --------------------------------------
# Optional: Live Grammar / Spelling Check
# --------------------------------------
from django.http import JsonResponse

@login_required
def live_check(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        score = evaluate_essay(text)
        return JsonResponse({"score": score})

    return JsonResponse({"error": "Invalid request"}, status=400)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UserTask
from .utils import evaluate_essay


@login_required
def submit_task(request):
    if request.method == "POST":
        title = request.POST.get("essay_title")
        text = request.POST.get("essay_text")

        result = evaluate_essay(text)

        task = UserTask.objects.create(
            user=request.user,
            essay_title=title,
            essay_text=text,
            score=result["score"],
            grammar_errors=result["grammar_errors"],
            spelling_errors=result["spelling_errors"],
            total_errors=result["total_errors"],
            word_count=result["word_count"],
        )

        # Redirect to score page with ID
        return redirect("tasks:score_page", task_id=task.id)

    return render(request, "submit_task.html")


@login_required
def score_page(request, task_id):

    task = UserTask.objects.get(id=task_id, user=request.user)

    context = {
        "user": request.user,
        "submission_date": task.submitted_at,
        "overall_score": task.score,
        "grammar_errors": task.grammar_errors,
        "spelling_errors": task.spelling_errors,
        "total_errors": task.total_errors,
        "essay_title": task.essay_title,
        "word_count": task.word_count,
    }

    return render(request, "score.html", context)


@login_required
def live_check(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        result = evaluate_essay(text)
        return JsonResponse(result)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def all_scores_page(request):

    if request.user.is_superuser:
        tasks = UserTask.objects.all().order_by("-submitted_at")
    else:
        tasks = UserTask.objects.filter(user=request.user).order_by("-submitted_at")

    return render(request, "all_scores.html", {"tasks": tasks})
