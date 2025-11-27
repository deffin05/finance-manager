import { useEffect, useState } from "react";
import { backendUrl } from "../App";

export default function Dashboard() {
    const [refreshKey, setRefreshKey] = useState(0);

    // 2. A function to toggle the state
    const refreshData = () => {
        setRefreshKey(oldKey => oldKey + 1);
    }

    return (
        <div>
            <Balance refreshTrigger={refreshKey} />
            <TransactionList refreshTrigger={refreshKey} />
            <TransactionForm onSuccess={refreshData} />
        </div>
    );
}

function Balance({ refreshTrigger }) {
    const [balance, setBalance] = useState(null);

    useEffect(() => {
        async function getBalance() {
            try {
                const balanceResponse = await fetch(backendUrl + 'balance/', {
                    method: "GET",
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access'),
                    },
                });
                const balanceJSON = await balanceResponse.json();
                if (!balanceJSON[0]) {
                    setBalance(0);
                } else {
                    // adjust this depending on the API shape; using first item or a value field
                    setBalance(balanceJSON[0].amount ?? balanceJSON[0]);
                }
            } catch (error) {
                console.error(error);
            }
        }
        getBalance();
    }, [refreshTrigger]);
    return (
        <>
            <h3>Balance: ${balance}</h3>
        </>
    )
}

function TransactionList({ refreshTrigger }) {
    const [transactions, setTransactions] = useState([]);

    useEffect(() => {
        async function getTransactions() {
            const transactionsResponse = await fetch(backendUrl + 'transactions/', {
                method: "GET",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
            }).catch((error) => console.error(error));

            const transactions = await transactionsResponse.json();
            setTransactions(transactions);
            console.log(transactions);
        }
        getTransactions();
    }, [refreshTrigger]);
    return (
        <>
            <h3>Transactions:</h3>
            <ul>
                {transactions.map((transaction) => (
                    <li key={transaction.id}>
                        ${transaction.amount} - {transaction.date}
                    </li>
                ))}
            </ul>
        </>
    )
}

function TransactionForm({ onSuccess }) {
    async function handleSubmit(event) {
        event.preventDefault();
        const data = JSON.stringify({
            ...Object.fromEntries(new FormData(document.forms['transactionForm']).entries()),
            currency: 'USD'
        });
        const response = await fetch(backendUrl + 'transactions/',
            {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
                body: data,
            }).catch((error) => console.error(error));

        if (response.ok) {
            onSuccess();
        }
    }
    return (
        <>
            <form id='transactionForm' style={{ display: 'flex', flexDirection: 'column', textAlign: 'left', gap: 4 }} onSubmit={handleSubmit}>
                <label form='amount'>Amount</label>
                <input type='number' name='amount' step={0.01} required />

                <input type='submit' value="Add transaction" />
            </form>
        </>
    )
}