import {Link, Route, Routes} from 'react-router-dom';
import './App.css'
import Login from "./pages/login.jsx"
import {useNavigate} from 'react-router-dom';
import {useEffect, useState} from 'react';
import {isLoggedIn} from './utils.js';
import Dashboard from './pages/Dashboard.jsx';
import {Settings} from "./pages/Settings.jsx";
import Signup from "./pages/Signup.jsx";

export const backendUrl = 'http://localhost:8000/';

function App() {
    const navigate = useNavigate();
    const [loggedIn, setLoggedIn] = useState(false);

    useEffect(() => {
        async function checkLogin() {
            if (location.pathname === "/login" || location.pathname === "/signup") return;
            if (!(await isLoggedIn())) {
                navigate("/login", {
                    replace: true
                })
            } else {
                setLoggedIn(true);
            }
        }

        checkLogin();
    }, [navigate])

    return (
        <>
            <nav>
                <Link to="/">Home</Link>
                {loggedIn ? (
                    <>
                        <Link to="/settings">Settings</Link>
                        <button onClick={() => {
                            localStorage.removeItem('access');
                            localStorage.removeItem('refresh');
                            setLoggedIn(false);
                            navigate("/login", {replace: true});
                        }}>Log out
                        </button>
                    </>
                ) : (
                    <Link to="/login">Log in</Link>
                )}
            </nav>
            <div id='content'>
                <Routes>
                    <Route path='/' element={<Dashboard/>}/>
                    <Route path='/login' element={<Login/>}/>
                    <Route path='/settings' element={<Settings/>}/>
                    <Route path='/signup' element={<Signup/>}/>
                </Routes>
            </div>
        </>
    )
}

export default App
