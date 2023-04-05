import pandas as pd
import numpy as np

# Read the data from downloaded csv file
data = pd.read_csv('C:/Users/Jason/Documents/DTU/KK/KK 29 regnskab - Alle_4_23.csv')

# Replace commas with dots and convert to float
data = data.replace(',','.', regex=True).astype(float)
data

# Extract total or first row and convert to numpy array
total = data.iloc[0].to_numpy()
payments = np.round(total - total.sum() / len(total), 2)  # Wh
print('total: ', total)
print('payments: ', payments)

tally = payments.copy()  # Copy of C to keep track of tally payments
transactions = np.ones((1, 3))
while min(transactions[:,2]) > 0:
    payer = np.argmin(tally)  # Biggest debt
    reciever = np.argmax(tally)  # Biggest credit
    
    # Calculate amount to pay
    limiter = abs(payments[payer]) - abs(payments[reciever])
    amount = abs(tally[reciever]) if limiter > 0 else abs(tally[payer])

    # Create transaction and update tally
    transaction = [payer, reciever, amount]
    transactions = np.vstack((transactions, transaction))
    tally[payer] += transaction[2]
    tally[reciever] -= transaction[2]

# Remove first and last row
transactions = transactions[1:-1]

names = data.columns
print("Payer\t\tReciever\tAmount")
for transaction in transactions:
    print(f"{names[int(transaction[0])]} \t {names[int(transaction[1])]} \t{np.round(transaction[2], 3)}")



