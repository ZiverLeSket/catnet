let httpRequest
let counter = 0

let feed = document.getElementById("feed")

feedUpdate()

window
.addEventListener("scrollend", () => {
    if (window.scrollY + window.innerHeight > document.documentElement.clientHeight - 200) {
        feedUpdate()
    }
});

async function feedUpdate() {
    curentdata = feed.innerHTML;
    if (curentdata === null) {
        curentdata = new String()
    }
    await fetch(`/feed-update/${counter}`)
    .then(response => response.json())
    .then(catdata => catdata.forEach(cat => curentdata = curentdata.concat(`<p class="center"><img src="/static/images/${cat.catid}.jpg" class="center"></p><p style="text-align: center;">${cat.description}</p>`)))
    .then(aboba => feed.innerHTML=curentdata)
    counter++
}