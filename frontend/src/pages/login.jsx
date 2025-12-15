import {Link, useNavigate} from "react-router-dom";
import {backendUrl} from "../App";
import {isLoggedIn} from "../utils";
import {useEffect} from "react";

function Login() {
    const navigate = useNavigate();

    async function handleSubmit(event) {
        event.preventDefault();
        const data = JSON.stringify(Object.fromEntries(new FormData(document.forms['loginForm']).entries()));
        const response = await fetch(backendUrl + 'auth/token/',
            {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: data,
            }).catch((error) => console.error(error));

        if (response.ok) {
            const responseJSON = await response.json()
            const accessToken = responseJSON["access"]
            const refreshToken = responseJSON["refresh"]

            localStorage.setItem("access", accessToken)
            localStorage.setItem("refresh", refreshToken)

            navigate("/", {
                replace: true
            })
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
            <form id='loginForm' style={{display: 'flex', flexDirection: 'column', textAlign: 'left', gap: 4}}
                  onSubmit={handleSubmit}>
                <label form='username'>Username</label>
                <input type='text' name='username' required/>

                <label form='password'>Password</label>
                <input type='password' name='password' required/>

                <div
                    style={{
                        display:"flex",
                        justifyContent:"space-between"
                    }}
                >
                    <Link to={"/signup"}>Sign up</Link>
                    <input type='submit'/>
                </div>
            </form>
        </>
    )
}

export default Login