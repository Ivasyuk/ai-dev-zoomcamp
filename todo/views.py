from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Todo

# Create your views here.

@login_required
def todo_list(request):
    """
    View to display all TODO items for the logged-in user.
    """
    todos = Todo.objects.filter(owner=request.user)
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        todos = todos.filter(status=status_filter)
    
    # Filter by priority if provided
    priority_filter = request.GET.get('priority')
    if priority_filter:
        todos = todos.filter(priority=priority_filter)
    
    context = {
        'todos': todos,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'todo/todo_list.html', context)


@login_required
def todo_detail(request, pk):
    """
    View to display a single TODO item.
    """
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    context = {'todo': todo}
    return render(request, 'todo/todo_detail.html', context)


@login_required
def todo_create(request):
    """
    View to create a new TODO item.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date')
        
        if title:
            todo = Todo.objects.create(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date if due_date else None,
                owner=request.user
            )
            messages.success(request, f'TODO "{todo.title}" created successfully!')
            return redirect('todo_list')
        else:
            messages.error(request, 'Title is required!')
    
    return render(request, 'todo/todo_form.html', {'action': 'Create'})


@login_required
def todo_update(request, pk):
    """
    View to update an existing TODO item.
    """
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        todo.title = request.POST.get('title', todo.title)
        todo.description = request.POST.get('description', todo.description)
        todo.status = request.POST.get('status', todo.status)
        todo.priority = request.POST.get('priority', todo.priority)
        due_date = request.POST.get('due_date')
        todo.due_date = due_date if due_date else None
        
        todo.save()
        messages.success(request, f'TODO "{todo.title}" updated successfully!')
        return redirect('todo_detail', pk=todo.pk)
    
    context = {
        'todo': todo,
        'action': 'Update'
    }
    return render(request, 'todo/todo_form.html', context)


@login_required
def todo_delete(request, pk):
    """
    View to delete a TODO item.
    """
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        title = todo.title
        todo.delete()
        messages.success(request, f'TODO "{title}" deleted successfully!')
        return redirect('todo_list')
    
    context = {'todo': todo}
    return render(request, 'todo/todo_confirm_delete.html', context)


@login_required
def todo_complete(request, pk):
    """
    View to mark a TODO as completed.
    """
    todo = get_object_or_404(Todo, pk=pk, owner=request.user)
    todo.mark_as_completed()
    messages.success(request, f'TODO "{todo.title}" marked as completed!')
    return redirect('todo_list')


@login_required
def todo_stats(request):
    """
    View to display statistics about the user's TODOs.
    """
    todos = Todo.objects.filter(owner=request.user)
    
    stats = {
        'total': todos.count(),
        'pending': todos.filter(status='pending').count(),
        'in_progress': todos.filter(status='in_progress').count(),
        'completed': todos.filter(status='completed').count(),
        'overdue': sum(1 for todo in todos if todo.is_overdue()),
        'high_priority': todos.filter(priority='high').count(),
    }
    
    context = {'stats': stats}
    return render(request, 'todo/todo_stats.html', context)
