import {useNavigate} from "react-router-dom";
import {backendUrl} from "../App";
import {isLoggedIn} from "../utils";
import {useEffect} from "react";

function Signup() {
    const navigate = useNavigate();

    async function handleSubmit(event) {
        event.preventDefault();

        const data = JSON.stringify(Object.fromEntries(new FormData(document.forms['signupForm']).entries()));

        const response = await fetch(backendUrl + 'auth/users/',
            {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: data,
            }).catch((error) => console.error(error));

        if (response.ok) {
            const responseJSON = await response.json()
            localStorage.setItem("access", responseJSON["access"])
            localStorage.setItem("refresh", responseJSON["refresh"])
            navigate("/", {replace: true})

        } else {
            console.error("Signup failed");
        }
    }

    useEffect(() => {
        async function checkLogin() {
            if (await isLoggedIn()) {
                navigate("/", {
                    replace: true
                })
            }
        }

        checkLogin();
    }, [navigate])


    return (
        <>
            <form id='signupForm' style={{display: 'flex', flexDirection: 'column', textAlign: 'left', gap: 4}}
                  onSubmit={handleSubmit}>
                <label htmlFor='username'>Username</label>
                <input type='text' name='username' required/>

                <label htmlFor='email'>Email</label>
                <input type='email' name='email' required/>

                <label htmlFor='password'>Password</label>
                <input type='password' name='password' required/>

                <input type='submit' value="Sign Up"/>
            </form>
        </>
    )
}

export default Signup