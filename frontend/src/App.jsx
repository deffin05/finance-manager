// import { useState } from 'react'
import './App.css'

const backendUrl = 'http://localhost:8000/';
function App() {
  return (
    <>
      <div className="card">
        <TransactionForm />
      </div>
    </>
  )
}

function TransactionForm() {

  function handleSubmit(event) {
    event.preventDefault();
    const data = JSON.stringify(Object.fromEntries(new FormData(document.forms['transactionForm']).entries()));
    fetch(backendUrl + 'transactions/',
      {
        method: "POST",
        headers: {
          'Content-Type': 'application/json'
        },
        body: data,
      }).catch((error) => console.error(error));
  }
  return (
    <>
      <form id='transactionForm' style={{ display: 'flex', flexDirection: 'column', textAlign: 'left', gap: 4 }} onSubmit={handleSubmit}>
        <label form='user'>User id</label>
        <input type='number' name='user' required />

        <label form='amount'>Amount</label>
        <input type='number' name='amount' step={0.01} required />

        <label form='currency'>Currency</label>
        <input type='text' name='currency' required minLength={3} maxLength={3} />

        <input type='submit' />
      </form>
    </>
  )
}

export default App
