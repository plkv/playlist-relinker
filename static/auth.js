// auth.js

window.addEventListener("DOMContentLoaded", () => {
  // Найдём кнопку входа
  const button = document.getElementById("loginButton");
  if (button) {
    button.addEventListener("click", () => {
      const clientId = "e727213173e141f482270557f6d11e26";
      const redirectUri = "https://exuberant-managers-615414.framer.app/setlink";
      const scopes = "playlist-read-private playlist-modify-private playlist-modify-public";

      const authUrl = `https://accounts.spotify.com/authorize?client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(
        redirectUri
      )}&scope=${encodeURIComponent(scopes)}`;

      window.location.href = authUrl;
    });
  }

  // Обработаем редирект от Spotify с ?code=...
  const params = new URLSearchParams(window.location.search);
  const code = params.get("code");

  if (code) {
    fetch("https://playlist-relinker.onrender.com/spotify/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.redirect) {
          window.location.href = data.redirect;
        } else {
          console.error("No redirect URL in response", data);
        }
      })
      .catch(err => {
        console.error("Error exchanging code:", err);
      });
  }
});
