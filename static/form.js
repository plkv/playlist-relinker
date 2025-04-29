window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search)
  const code = params.get("code")

  // Если URL содержит код от Spotify — обмениваем на access_token
  if (code) {
    fetch("https://playlist-relinker.onrender.com/spotify/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code })
    })
      .then(res => res.json())
      .then(data => {
        localStorage.setItem("access_token", data.access_token)
      })
      .catch(err => console.error("Auth error:", err))
  }

  const input = document.getElementById("playlistInput")
  const button = document.getElementById("rebuildButton")

  button?.addEventListener("click", () => {
    const url = input?.value
    const token = localStorage.getItem("access_token")
    if (!url || !token) return

    fetch("https://playlist-relinker.onrender.com/fetch-tracks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, access_token: token })
    })
      .then(res => res.json())
      .then(data => {
        localStorage.setItem("tracks", JSON.stringify(data.tracks))
        window.location.href = "/results"
      })
      .catch(err => console.error("Fetch error:", err))
  })
})
