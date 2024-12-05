from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Transaction, Budget
from .forms import TransactionForm, BudgetForm

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transactions/transaction_list.html', {
        'transactions': transactions
    })

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            try:
                transaction.save()
                messages.success(request, 'Transaction added successfully!')
                return redirect('transactions:transactions')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = TransactionForm()
    
    return render(request, 'transactions/transaction_form.html', {
        'form': form,
        'action': 'Add'
    })

@login_required
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    old_amount = transaction.amount
    old_type = transaction.transaction_type
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            try:
                new_amount = form.cleaned_data['amount']
                new_type = form.cleaned_data['transaction_type']
                
                budget = Budget.objects.filter(user=request.user).first()
                if budget:
                    # Handle type change from expense to income
                    if old_type == 'expense' and new_type == 'income':
                        budget.current_balance += old_amount  # Add back the old expense
                        budget.current_balance += new_amount  # Add the new income
                    
                    # Handle type change from income to expense
                    elif old_type == 'income' and new_type == 'expense':
                        budget.current_balance -= old_amount  # Remove the old income
                        budget.current_balance -= new_amount  # Subtract the new expense
                    
                    # Handle amount change for expense
                    elif old_type == 'expense' and new_type == 'expense':
                        budget.current_balance += old_amount  # Add back the old expense
                        budget.current_balance -= new_amount  # Subtract the new expense
                    
                    # Handle amount change for income
                    elif old_type == 'income' and new_type == 'income':
                        budget.current_balance -= old_amount  # Remove the old income
                        budget.current_balance += new_amount  # Add the new income
                    
                    budget.save()
                
                form.save()
                messages.success(request, 'Transaction updated successfully!')
                return redirect('transactions:transactions')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error updating transaction: {str(e)}')
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'transactions/transaction_form.html', {
        'form': form,
        'action': 'Edit',
        'transaction': transaction
    })


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transactions:transactions')
    return render(request, 'transactions/transaction_confirm_delete.html', {
        'transaction': transaction
    })



@login_required
def set_budget(request):
    # Get current budget for the user if it exists
    current_budget = Budget.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        try:
            budget_amount = float(request.POST.get('budget_amount', 0))
            budget_month = request.POST.get('budget_month')
            category = request.POST.get('category')

            # Validate all required fields
            if not all([budget_amount, budget_month, category]):
                messages.error(request, 'Please fill in all required fields')
                return redirect('transactions:set_budget')

            if budget_amount <= 0:
                messages.error(request, 'Budget amount must be greater than 0')
                return redirect('transactions:set_budget')
            
            if current_budget:
                # Update existing budget
                current_budget.amount = budget_amount
                current_budget.month = budget_month
                current_budget.category = category
                current_budget.save()
                messages.success(request, 'Budget updated successfully!')
            else:
                # Create new budget
                Budget.objects.create(
                    user=request.user,
                    amount=budget_amount,
                    month=budget_month,
                    category=category
                )
                messages.success(request, 'Budget set successfully!')
            
            return redirect('transactions:transactions')
            
        except ValueError:
            messages.error(request, 'Please enter a valid number')
            return redirect('transactions:set_budget')
    
    context = {
        'current_budget': current_budget
    }
    return render(request, 'transactions/set_budget.html', context)



@login_required
def transaction_delete(request, pk):
    # Get the transaction or return 404 if not found
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        try:
            # Store transaction details for the success message
            amount = transaction.amount
            date = transaction.date
            
            # Delete the transaction
            transaction.delete()
            
            messages.success(
                request,
                f'Transaction of ${amount} from {date} was successfully deleted.'
            )
            return redirect('transactions:transactions')
            
        except Exception as e:
            messages.error(
                request,
                'An error occurred while deleting the transaction. Please try again.'
            )
            return redirect('transactions:transactions')
    
    return render(request, 'transactions/transaction_confirm_delete.html', {
        'transaction': transaction
    })