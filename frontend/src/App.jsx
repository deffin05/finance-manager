// import { useState } from 'react'
import { Link, Route, Routes } from 'react-router-dom';
import './App.css'
import Login from "./pages/login.jsx"
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { isLoggedIn } from './utils.js';

export const backendUrl = 'http://localhost:8000/';
function App() {
  const navigate = useNavigate();

  useEffect(() => {
    async function checkLogin() {
      if (!(await isLoggedIn())) {
        navigate("/login", {
          replace: true
        })
      }
    }
    checkLogin();
  }, [navigate])

  return (
    <>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/login">Log in</Link>
      </nav>
      <div id='content'>
        <Routes>
          <Route path='/' element={<TransactionForm />} />
          <Route path='/login' element={<Login />} />
        </Routes>
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
