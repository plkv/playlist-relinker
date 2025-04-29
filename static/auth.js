function waitForLoginButton() {
  const button = document.getElementById("loginButton")
  if (!button) {
    setTimeout(waitForLoginButton, 100) // пробуем снова через 100мс
    return
  }

  button.addEventListener("click", () => {
    const clientId = "e727213173e141f482270557f6d11e26"
    const redirectUri = "https://exuberant-managers-615414.framer.app/setlink"
    const scopes = "playlist-read-private"

    const authUrl = `https://accounts.spotify.com/authorize?client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scopes)}`
    window.location.href = authUrl
  })
}

waitForLoginButton()