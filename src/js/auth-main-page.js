

function isLogin()
{
    if (sessionStorage.getItem('access-token') || localStorage.getItem('refresh-token'))
    {
        document.getElementById('signOn').style.display = 'none';
        document.getElementById('signIn').style.display = 'none';
    }
    else
    {
        document.getElementById('signOut').style.display = 'none';
    }
}
function logout()
{
    sessionStorage.removeItem('access-token');
    localStorage.removeItem('refresh-token');
    window.location.href = 'http://localhost:3001/checker';
}

