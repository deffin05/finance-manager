import { useEffect, useState } from "react";
import { backendUrl } from "../App";
import DeleteIcon from './../assets/delete.svg';
import EditIcon from './../assets/edit.svg';

export default function Dashboard() {
    const [refreshKey, setRefreshKey] = useState(0);

    // 2. A function to toggle the state
    const refreshData = () => {
        setRefreshKey(oldKey => oldKey + 1);
    }

    return (
        <div>
            <Balance refreshTrigger={refreshKey} />
            <TransactionList refreshTrigger={refreshKey} refreshFunction={refreshData} />
            <TransactionForm refreshFunction={refreshData} />
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
                    setBalance(new Intl.NumberFormat("en-US", { minimumFractionDigits: 2 }).format(balanceJSON[0].amount) ?? balanceJSON[0]);
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

function TransactionList({ refreshTrigger, refreshFunction }) {
    const [transactions, setTransactions] = useState([]);

    const [editRowId, setEditRowId] = useState(null);
    const [formData, setFormData] = useState({ amount: 0, date: "", currency: "USD" });

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
            setTransactions(transactions.results);
        }
        getTransactions();
    }, [refreshTrigger]);

    const handleEditClick = (transaction) => {
        setEditRowId(transaction.id);
        setFormData({ amount: transaction.amount, date: transaction.date, currency: "USD" });
    };

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSave = async (transaction) => {
        if (formData.amount == transaction.amount && formData.date == transaction.date) {
            setEditRowId(null);
            return;
        }
        try {
            const response = await fetch(`${backendUrl}transactions/${transaction.id}/`, {
                method: "PUT",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                setEditRowId(null);
                refreshFunction();
            } else {
                console.error("Failed to save");
            }
        } catch (error) {
            console.error(error);
        }
    };

    const handleCancel = () => {
        setEditRowId(null);
    };

    return (
        <>
            <h3>Transactions:</h3>
            <table>
                <thead>
                    <tr>
                        <th>Amount</th>
                        <th>Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {transactions.map((transaction) => {
                        const isEditing = editRowId === transaction.id;

                        return (
                            <tr key={transaction.id}>
                                <td>
                                    {isEditing ? (
                                        <>
                                            $<input
                                                type="number"
                                                name="amount"
                                                step={0.01}
                                                value={formData.amount}
                                                onChange={handleInputChange}
                                            />
                                        </>
                                    ) : (
                                        `$${new Intl.NumberFormat("en-US", { minimumFractionDigits: 2 }).format(transaction.amount)}`
                                    )}
                                </td>
                                <td>
                                    {isEditing ? (
                                        <input
                                            type="date"
                                            name="date"
                                            value={formData.date}
                                            onChange={handleInputChange}
                                        />
                                    ) : (
                                        new Date(transaction.date).toLocaleString()
                                    )}
                                </td>
                                <td>
                                    <div style={{ display: "flex", gap: "8px" }}>
                                        {isEditing ? (
                                            <>
                                                <button onClick={() => handleSave(transaction)} className="iconButton editButton">
                                                    Save
                                                </button>
                                                <button onClick={handleCancel} className="iconButton deleteButton" style={{ width: 72 }}>
                                                    Cancel
                                                </button>
                                            </>
                                        ) : (
                                            <>
                                                <EditButton onClick={() => handleEditClick(transaction)} />

                                                <DeleteButton
                                                    transaction={transaction}
                                                    refreshFunction={refreshFunction}
                                                />
                                            </>
                                        )}
                                    </div>
                                </td>
                            </tr>
                        )
                    })}
                </tbody>
            </table>
        </>
    )
}

function TransactionForm({ refreshFunction }) {
    async function handleSubmit(event) {
        event.preventDefault();
        const data = JSON.stringify(Object.fromEntries(new FormData(document.forms['transactionForm']).entries()));
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
            refreshFunction();
        }
    }
    return (
        <>
            <form id='transactionForm' onSubmit={handleSubmit}>
                <div>
                    <label form='currency'>Currency</label>
                    <select name="currency" id="currency" required>
                        <option value="USD">USD</option>
                        <option value="EUR">EUR</option>
                        <option value="UAH">UAH</option>
                    </select>
                </div>
                <div>
                    <label form='amount'>Amount</label>
                    <input type='number' name='amount' step={0.01} required />
                </div>
                <input type='submit' value="Add transaction" />
            </form >
        </>
    )
}

function EditButton({ onClick }) {

    return (
        <>
            <button className="editButton iconButton" onClick={onClick}><img src={EditIcon} className="icon" /></button>
        </>
    )
}

function DeleteButton({ transaction, refreshFunction }) {

    async function handle(event) {
        event.preventDefault();
        const response = await fetch(backendUrl + `transactions/${transaction.id}/`,
            {
                method: "DELETE",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
            }).catch((error) => console.error(error));

        if (response.ok) {
            refreshFunction();
        }
    }

    return (
        <>
            <button className="deleteButton iconButton" onClick={handle}><img src={DeleteIcon} className="icon" /></button>
        </>
    )
}