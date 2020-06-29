const burger = document.getElementById("burger");
const navslide = document.getElementById("navmenu2");
burger.addEventListener("click", () =>{
    navslide.classList.toggle("navmenu2-active");
});


const modal1 = document.querySelector(".modal1");
document.getElementById("referallink").addEventListener("click", ()=>{
    modal1.classList.toggle("modalvisible");
});
document.getElementById("close").addEventListener("click", ()=>{
    modal1.classList.toggle("modalvisible");
});