import {backendUrl} from "../App.jsx";
import {useEffect, useState} from "react";
import DeleteIcon from "../assets/delete.svg";

export function Settings() {
    const [hasToken, setHasToken] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);


    const refreshData = () => {
        setRefreshKey(oldKey => oldKey + 1);
    }

    useEffect(() => {
        async function onLoad() {
            const response = await fetch(backendUrl + 'monobank/verify/',
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access'),
                    },
                })
            if (response.ok) {
                setHasToken(true)
            } else {
                setHasToken(false)
            }
        }

        onLoad();
    }, [refreshKey])

    return (
        <>
            <div
                style={{
                    display: "flex",
                    flexDirection: "column"
                }}
            >
                <TokenForm disable={hasToken} refreshFunction={setRefreshKey}/>
                {hasToken ? <BalanceList/> : <></>}
            </div>
        </>
    )
}


function TokenForm({disable, refreshFunction}) {
    const [secretValue, setSecretValue] = useState("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    async function handleSubmit(event) {
        event.preventDefault();
        let form = JSON.stringify(Object.fromEntries(new FormData(document.forms['tokenForm']).entries()));

        const response = await fetch(backendUrl + 'monobank/token/',
            {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
                body: form,
            }).catch((error) => console.error(error));

        if (response.ok) {
            refreshFunction()
        }
    }

    async function deleteToken(event) {
        event.preventDefault()
        const response = await fetch(backendUrl + 'monobank/token/',
            {
                method: "DELETE",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                }
            }).catch((error) => console.error(error));

        if (response.ok) {
            setSecretValue("")
            refreshFunction()
        }
    }

    return (
        <>
            <div>
                <form
                    id="tokenForm"
                    className={"verticalForm"}
                    onSubmit={handleSubmit}
                >
                    <label
                        style={{
                            fontSize: "1.2em"
                        }}
                        form="token"
                    >Monobank token</label>
                    <div
                        style={{
                            display: "flex",
                            width: "100%",
                            gap: "5px"
                        }}>
                        {
                            disable ?
                                <>
                                    <input
                                        className={"modalInput"}
                                        type="password"
                                        name="token"
                                        value={secretValue}
                                        style={{
                                            minWidth: "20vw",
                                            width: "50ch",
                                        }}
                                        disabled
                                    />
                                    <button className="deleteButton iconButton" onClick={deleteToken}>
                                        <img src={DeleteIcon} className="icon"/>
                                    </button>

                                </> :
                                <>
                                    <input
                                        className={"modalInput"}
                                        type="text"
                                        name="token"
                                        style={{
                                            minWidth: "20vw",
                                            width: "50ch",
                                        }}
                                    />
                                    <input
                                        type="submit"
                                        value="Submit"
                                        style={{
                                            backgroundColor: "#38ed38",
                                            color: "black",
                                            padding: "8px",
                                            borderRadius: "5px",
                                            fontSize: "1.2em"
                                        }}
                                    />
                                </>
                        }
                    </div>
                </form>
            </div>
        </>
    )
}

function BalanceList() {
    const [balances, setBalances] = useState([]);

    useEffect(() => {
        async function getBalances() {
            const response = await fetch(backendUrl + "monobank/balances/",
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access'),
                    }
                })

            const responseJson = await response.json()
            setBalances(responseJson)
        }

        getBalances()
    }, [])

    async function handleCheckboxChange(id, current) {
        const response = await fetch(backendUrl + `monobank/balances/${id}/`,
            {
                method: "PATCH",
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access'),
                },
                body: JSON.stringify({"watch": !current})
            })
    }

    return (
        <>
            <h2>Balance list:</h2>
            <table>
                <thead>
                <tr>
                    <th>Name</th>
                    <th>Amount</th>
                    <th>Currency</th>
                    <th>Track</th>
                </tr>
                </thead>
                <tbody>
                {balances.map((b) => {
                    return (
                        <>
                            <tr key={b.id}>
                                <td>{b.name}</td>
                                <td>{b.currency}</td>
                                <td>{new Intl.NumberFormat('en-US', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2,
                                }).format(b.amount)}</td>
                                <td>
                                    <input
                                        type={"checkbox"}
                                        defaultChecked={b.watch}
                                        onChange={() => handleCheckboxChange(b.id, b.watch)}
                                    />
                                </td>
                            </tr>
                        </>
                    )
                })}
                </tbody>
            </table>
        </>
    )
}