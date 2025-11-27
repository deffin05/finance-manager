import { backendUrl } from "./App";

export async function isLoggedIn() {
    const accessToken = localStorage.getItem("access");
    if (!accessToken) {
        return false;
    }

    const verifyAccessToken = await fetch(backendUrl + 'auth/token/verify/',
        {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ "token": accessToken }),
        }).catch((error) => console.error(error));

    if (verifyAccessToken.ok) {
        return true;
    }

    const refreshToken = localStorage.getItem("refresh");
    if (!refreshToken) {
        return false;
    }

    const refreshAccessToken = await fetch(backendUrl + 'auth/token/refresh/',
        {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ "refresh": refreshToken }),
        }).catch((error) => console.error(error));

    if (refreshAccessToken.ok) {
        const responseJSON = await refreshAccessToken.json()
        const newAccessToken = responseJSON["access"]
        localStorage.setItem("access", newAccessToken)
        return true;
    }

    localStorage.removeItem("access");
    localStorage.removeItem("refresh");

    return false;
}