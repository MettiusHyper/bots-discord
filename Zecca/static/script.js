var withQuery = window.matchMedia("(max-width: 767px)")
var dropdownOpen = false;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function openDropdown() {
    var lambda = document.getElementsByClassName("dropdown")[0];
    if (lambda.style.display === "none") {
        lambda.style.display = "block";
        lambda.style.animationName = "slide";
        await sleep(1100)
        lambda.style.animationName = "none";
        dropdownOpen = true;
    } else {
        if(lambda.style.display.toString === "") {
            lambda.style.display = "block";
            dropdownOpen = true;
        } else {
            lambda.style.display = "none";
            dropdownOpen = false;
        }
    }
}

function resizeDropdown() {
    var lambda = document.getElementsByClassName("dropdown")[0];
    if (withQuery.matches) { // If media query matches
        if (dropdownOpen === false) {
            lambda.style.display = "none";
        }
        
    } else {
        lambda.style.display = "flex";
        dropdownOpen = false;
    }
}

function open_download(){
    document.getElementById("list").style.display = "none";
    document.getElementById("par").style.display = "block";
}

function close_download(){
    document.getElementById("list").style.display = "block";
    document.getElementById("par").style.display = "none";
}

window.addEventListener("resize", resizeDropdown)
window.addEventListener("load", resizeDropdown)