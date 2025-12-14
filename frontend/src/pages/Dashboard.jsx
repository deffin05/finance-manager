import {useEffect, useState} from "react";
import {backendUrl} from "../App";
import DeleteIcon from './../assets/delete.svg';
import EditIcon from './../assets/edit.svg';

async function getBalances(setBalances, setBalanceId, setCurrency, loaded) {
    try {
        const response = await fetch(backendUrl + 'balance/', {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('access'),
            },
        });
        const balances = await response.json();
        setBalances(balances);
        if (!loaded && balances.length > 0) {
            setBalanceId(balances[0].id)
            setCurrency(balances[0].currency)
        }
    } catch (error) {
        console.error(error);
    }
}

export default function Dashboard() {
    const [refreshKey, setRefreshKey] = useState(0);
    const [balanceId, setBalanceId] = useState("");
    const [currency, setCurrency] = useState('');
    const [balances, setBalances] = useState([]);
    const [isBalancesLoaded, setIsBalancesLoaded] = useState(false);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);

    const refreshData = () => {
        setRefreshKey(oldKey => oldKey + 1);
    }

    useEffect(() => {
        async function load() {
            await getBalances(setBalances, setBalanceId, setCurrency, isBalancesLoaded);
            setIsBalancesLoaded(true)
        }

        load()
    }, [refreshKey])

    async function handleFileChange(event) {
        event.preventDefault()
        const formData = new FormData()
        const file = event.target.files[0];

        formData.append('file', file)

        const response = await fetch(backendUrl + `import/?balance_id=${balanceId}`, {
            method: "POST",
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access'),
            },
            body: formData
        })

        if (response.ok) {
            refreshData()
        }
    }

    async function handleDeleteBalance(event) {
        event.preventDefault()

        const response = await fetch(backendUrl + `balance/${balanceId}/`,
            {
                method: "DELETE",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
            }).catch((error) => console.error(error));

        if (response.ok) {
            setIsBalancesLoaded(false)
            refreshData()
        }
    }

    async function handleEditBalance(event) {
        event.preventDefault();
        if (balanceId) {
            setIsEditModalOpen(true);
        }
    }

    return (
        <div>
            {isBalancesLoaded ?
                <>
                    <div
                        style={{
                            display: "flex",
                            justifyContent: "space-between"
                        }}
                    >
                        <input
                            type={"file"}
                            id={"fileUpload"}
                            onChange={handleFileChange}
                            hidden
                        />
                        <label
                            htmlFor={"fileUpload"}
                            style={{
                                backgroundColor: "#222",
                                color: "#fff",
                                padding: "8px",
                                borderRadius: "4px",
                                cursor: "pointer"
                            }}
                        >Upload payment statement</label>

                        <div
                            style={{
                                display: "flex",
                                gap: "8px"
                            }}>
                            <button
                                style={{
                                    backgroundColor: "#00c"
                                }}
                                onClick={handleEditBalance}
                            >Edit
                            </button>
                            <button
                                style={{
                                    backgroundColor: "#c00"
                                }}
                                onClick={handleDeleteBalance}
                            >Delete
                            </button>
                        </div>
                    </div>
                    <Balance
                        refreshTrigger={refreshKey}
                        balanceId={balanceId}
                        refreshFunction={refreshData}
                        setBalanceId={setBalanceId}
                        currency={currency}
                        setCurrency={setCurrency}
                        balances={balances}
                    />
                    <TransactionList
                        refreshTrigger={refreshKey}
                        refreshFunction={refreshData}
                        balanceId={balanceId}
                        currency={currency}
                    />
                    <TransactionForm refreshFunction={refreshData} balanceId={balanceId}/>
                    <EditBalanceModal
                        isOpen={isEditModalOpen}
                        onClose={() => setIsEditModalOpen(false)}
                        onUpdated={refreshData}
                        balanceToEdit={balances.find(b => b.id.toString() === balanceId.toString())}
                    />
                </> :
                <p>Loading...</p>
            }
        </div>
    );
}

function Balance({refreshTrigger, balanceId, refreshFunction, setBalanceId, currency, setCurrency, balances}) {
    const [currentAmount, setCurrentAmount] = useState(0);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        if (balances.length === 0) {
            setIsModalOpen(true);
            setCurrentAmount(0);
        }
    }, [refreshTrigger]);

    useEffect(() => {
        if (!balances.length) {
            setCurrentAmount(0);
            return;
        }
        const selected = balances.find(b => b.id.toString() === balanceId.toString());
        setCurrentAmount(selected ? selected.amount : 0);
        setCurrency(selected.currency)
    }, [balanceId, balances]);

    return (
        <>
            <h3>Balance: </h3>

            <CustomDropdown
                options={balances}
                selectedId={balanceId}
                onChange={setBalanceId}
                openModal={setIsModalOpen}
                refreshFunction={refreshFunction}
            />

            <h2>
                {new Intl.NumberFormat("en-US", {minimumFractionDigits: 2}).format(currentAmount)} {currency}
            </h2>

            <CreateBalanceModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreated={refreshFunction}
            />
        </>
    )
}

function formatDecimalString(number) {
    let split = number.split('.')
    while (split[1].length > 2 && split[1].charAt(split[1].length - 1) === "0") {
        split[1] = split[1].slice(0, -1)
    }

    return split.join('.')
}

function TransactionList({refreshTrigger, refreshFunction, currency, balanceId}) {
    const [transactions, setTransactions] = useState([]);

    const [nextPageUrl, setNextPageUrl] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const [editRowId, setEditRowId] = useState(null);
    const [formData, setFormData] = useState({amount: 0, date: "", currency: "USD"});

    async function getTransactions(url, isLoadMore = false) {
        setIsLoading(true);
        try {
            const transactionsResponse = await fetch(url, {
                method: "GET",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
            }).catch((error) => console.error(error));

            const transactions = await transactionsResponse.json();
            if (isLoadMore) {
                setTransactions(prev => [...prev, ...transactions.results]);
            } else {
                setTransactions(transactions.results);
            }

            setNextPageUrl(transactions.next);
        } catch (error) {
            console.error(error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        getTransactions(backendUrl + `balance/${balanceId}/transactions/`, false);
    }, [refreshTrigger]);

    function handleLoadMore() {
        if (nextPageUrl) {
            getTransactions(nextPageUrl, true);
        }
    }

    const handleEditClick = (transaction) => {
        setEditRowId(transaction.id);
        let local_date = new Date(transaction.date);
        local_date.setMinutes(local_date.getMinutes() - local_date.getTimezoneOffset())
        setFormData({amount: transaction.amount, date: local_date.toISOString().slice(0, 19), currency: "USD"});
    };

    const handleInputChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const handleSave = async (transaction) => {
        let utc_date = new Date(formData.date).toISOString();

        if (formData.amount == transaction.amount && utc_date.slice(0, 19) == transaction.date.slice(0, 19)) {
            setEditRowId(null);
            return;
        }
        try {
            const response = await fetch(`${backendUrl}transactions/${transaction.id}/`, {
                method: "PATCH",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
                body: JSON.stringify({...formData, date: utc_date})
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
            <table>
                <thead>
                <tr>
                    <th>Category</th>
                    <th>Description</th>
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
                            <td>{transaction.category}</td>
                            <td>{transaction.name}</td>
                            <td>
                                {isEditing ? (
                                    <>
                                        <input
                                            type="number"
                                            name="amount"
                                            step={0.01}
                                            value={formatDecimalString(formData.amount)}
                                            onChange={handleInputChange}
                                        />
                                    </>
                                ) : (
                                    `${new Intl.NumberFormat("en-US", {minimumFractionDigits: 2}).format(transaction.amount)} ${currency}`
                                )}
                            </td>
                            <td>
                                {isEditing ? (
                                    <input
                                        type="datetime-local"
                                        name="date"
                                        step={1}
                                        value={formData.date}
                                        onChange={handleInputChange}
                                    />
                                ) : (
                                    new Date(transaction.date).toLocaleString()
                                )}
                            </td>
                            <td>
                                <div style={{display: "flex", gap: "8px"}}>
                                    {isEditing ? (
                                        <>
                                            <button onClick={() => handleSave(transaction)}
                                                    className="iconButton editButton">
                                                Save
                                            </button>
                                            <button onClick={handleCancel} className="iconButton deleteButton"
                                                    style={{width: 72}}>
                                                Cancel
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <EditButton onClick={() => handleEditClick(transaction)}/>

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

            <div style={{marginTop: '20px', textAlign: 'center'}}>
                {isLoading && <p>Loading...</p>}

                {!isLoading && nextPageUrl && (
                    <button
                        onClick={handleLoadMore}
                        style={{padding: '10px 20px', cursor: 'pointer'}}
                    >
                        Load More
                    </button>
                )}
            </div>

        </>
    )
}

function TransactionForm({refreshFunction, balanceId}) {
    async function handleSubmit(event) {
        event.preventDefault();
        const data = JSON.stringify({
            ...Object.fromEntries(new FormData(document.forms['transactionForm']).entries()),
            "category": "-"
        });
        const response = await fetch(backendUrl + `balance/${balanceId}/transactions/`,
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
                    <label form='amount'>Amount</label>
                    <input type='number' name='amount' step={0.01} required/>
                </div>
                <input type='submit' value="Add transaction"/>
            </form>
        </>
    )
}

function EditButton({onClick}) {

    return (
        <>
            <button className="editButton iconButton" onClick={onClick}><img src={EditIcon} className="icon"/></button>
        </>
    )
}

function DeleteButton({transaction, refreshFunction}) {

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
            <button className="deleteButton iconButton" onClick={handle}><img src={DeleteIcon} className="icon"/>
            </button>
        </>
    )
}

function CreateBalanceModal({isOpen, onClose, onCreated}) {
    const [name, setName] = useState("");
    const [currency, setCurrency] = useState("USD");
    const [initialAmount, setInitialAmount] = useState(0);

    if (!isOpen) return null;

    async function handleSubmit(e) {
        e.preventDefault();
        let balanceName = name
        if (balanceName === "") {
            balanceName = `${currency} balance`
        }
        try {
            const response = await fetch(backendUrl + 'balance/', { // Adjust URL if different
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
                body: JSON.stringify({
                    name: balanceName,
                    currency: currency,
                    amount: initialAmount
                })
            });

            if (response.ok) {
                onCreated();
                onClose();
            } else {
                alert("Failed to create balance");
            }
        } catch (error) {
            console.error(error);
        }
    }

    return (
        <div className={"modalOverlay"}>
            <div className={"modalContent"}>
                <h2>Create new balance</h2>

                <form className={"verticalForm"} onSubmit={handleSubmit}>
                    <div>
                        <label
                            className={"modalLabel"}
                            form="name">
                            Name<span style={{"color": "#777", "fontSize": "0.8em"}}> (optional)</span>:
                        </label>
                        <input
                            className={"modalInput"}
                            name="name"
                            type="text"
                            value={name}
                            onChange={e => setName(e.target.value)}
                        />
                    </div>
                    <div>
                        <label
                            className={"modalLabel"}
                            form="currency">
                            Currency:
                        </label>
                        <select
                            name="currency"
                            className={"modalInput"}
                            value={currency}
                            onChange={e => setCurrency(e.target.value)}
                        >
                            <option value="USD">USD</option>
                            <option value="EUR">EUR</option>
                            <option value="UAH">UAH</option>
                        </select>
                    </div>

                    <div>
                        <label
                            className={"modalLabel"}
                            form="amount">
                            Initial amount:
                        </label>
                        <input
                            className={"modalInput"}
                            type="number"
                            name="amount"
                            placeholder="Initial Amount"
                            value={initialAmount}
                            onChange={e => setInitialAmount(e.target.value)}
                            step="0.01"
                        />
                    </div>
                    <button type="submit" style={{cursor: 'pointer', backgroundColor: '#7e854b', border: 'none'}}>
                        Create Account
                    </button>
                </form>
            </div>
        </div>
    );
}


function CustomDropdown({options, selectedId, onChange, openModal, refreshFunction}) {
    const [isOpen, setIsOpen] = useState(false);
    const selectedItem = options.find(o => o.id.toString() === selectedId.toString());

    return (
        <div className={"balanceDisplayParent"}>

            <div
                onClick={() => setIsOpen(!isOpen)}
                className={"balanceDisplay"}
            >
                <span>
                    {selectedItem
                        ? `${selectedItem.currency} - ${selectedItem.name}`
                        : "All Accounts"}
                </span>
                <span style={{fontSize: '0.8em', marginLeft: '10px'}}>▼</span>
            </div>

            {isOpen && (
                <>
                    {/* Invisible overlay to close menu when clicking outside */}
                    <div
                        style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 1}}
                        onClick={() => setIsOpen(false)}
                    />

                    <ul className={"balanceList"}>
                        {options.map((b) => (
                            <li
                                key={b.id}
                                className={"balanceItem"}
                                onClick={() => {
                                    onChange(b.id);
                                    setIsOpen(false);
                                    refreshFunction()
                                }}
                                style={{
                                    backgroundColor: selectedId === b.id ? '#fff2dc' : 'white',
                                }}
                            >
                                <div style={{fontWeight: 'bold', fontSize: '1rem'}}>
                                    {b.name} ({b.currency})
                                </div>
                                <div style={{color: '#666', fontSize: '0.85rem'}}>
                                    Balance: {new Intl.NumberFormat("en-US", {minimumFractionDigits: 2}).format(b.amount)}
                                </div>
                            </li>
                        ))}
                        <li
                            onClick={() => {
                                setIsOpen(false);
                                openModal(true)
                            }}
                            className={"balanceItem"}
                            style={{
                                backgroundColor: 'white'
                            }}
                        >
                            <span style={{fontWeight: 'bold'}}>Create new balance</span>
                        </li>
                    </ul>
                </>
            )}
        </div>
    );
}

function EditBalanceModal({isOpen, onClose, onUpdated, balanceToEdit}) {
    const [name, setName] = useState("");
    const [currency, setCurrency] = useState("USD");
    const [amount, setAmount] = useState(0);

    // Pre-fill form when the modal opens or the selected balance changes
    useEffect(() => {
        if (isOpen && balanceToEdit) {
            setName(balanceToEdit.name);
            setCurrency(balanceToEdit.currency);
            setAmount(formatDecimalString(balanceToEdit.amount));
        }
    }, [isOpen, balanceToEdit]);

    if (!isOpen) return null;

    async function handleSubmit(e) {
        e.preventDefault();

        try {
            const response = await fetch(backendUrl + `balance/${balanceToEdit.id}/`, {
                method: "PATCH",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
                body: JSON.stringify({
                    name: name,
                    currency: currency,
                    amount: amount
                })
            });

            if (response.ok) {
                onUpdated();
                onClose();
            }
        } catch (error) {
            console.error(error);
        }
    }

    return (
        <div className={"modalOverlay"}>
            <div className={"modalContent"}>
                <h2>Edit Balance</h2>

                <form className={"verticalForm"} onSubmit={handleSubmit}>
                    <div>
                        <label className={"modalLabel"}>
                            Name:
                        </label>
                        <input
                            className={"modalInput"}
                            type="text"
                            value={name}
                            onChange={e => setName(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className={"modalLabel"}>
                            Currency:
                        </label>
                        <select
                            className={"modalInput"}
                            value={currency}
                            onChange={e => setCurrency(e.target.value)}
                        >
                            <option value="USD">USD</option>
                            <option value="EUR">EUR</option>
                            <option value="UAH">UAH</option>
                        </select>
                    </div>

                    <div>
                        <label className={"modalLabel"}>
                            Amount:
                        </label>
                        <input
                            className={"modalInput"}
                            type="number"
                            value={amount}
                            onChange={e => setAmount(e.target.value)}
                            step="0.01"
                        />
                    </div>

                    <div style={{display: 'flex', gap: '10px', marginTop: '10px'}}>
                        <button type="submit" style={{backgroundColor: '#070', border: 'none', padding: '8px 16px'}}>
                            Save Changes
                        </button>
                        <button type="button" onClick={onClose}
                                style={{backgroundColor: '#700', border: 'none', padding: '8px 16px'}}>
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}