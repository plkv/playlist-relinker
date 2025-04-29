window.addEventListener("DOMContentLoaded", () => {
  const list = document.getElementById("trackList")
  const template = document.getElementById("trackTemplate")
  if (!list || !template) return

  const tracks = JSON.parse(localStorage.getItem("tracks") || "[]")

  tracks.forEach(track => {
    const clone = template.cloneNode(true)
    clone.id = ""
    clone.style.opacity = "1"
    clone.style.visibility = "visible"
    clone.classList.add("track")
    clone.dataset.id = track.id
    clone.dataset.name = track.matched

    const originalEl = clone.querySelector("#originalTrack")
    const foundEl = clone.querySelector("#foundTrack")
    if (originalEl) originalEl.textContent = track.original
    if (foundEl) foundEl.textContent = track.matched

    clone.addEventListener("click", () => {
      fetch("https://playlist-relinker.onrender.com/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: track.id })
      })
    })

    list.appendChild(clone)
  })
})
