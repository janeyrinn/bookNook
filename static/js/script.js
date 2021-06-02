// initializes book icon to open sidenav: 
$(document).ready(function () {
  $('.sidenav').sidenav({
    edge: "right"
  });
});

// generates date for copywrite in footer
$("#copyright").text(new Date().getFullYear());

// facilitates typewriter text effect on homepage(accredited to W3 Schools)
var i = 0;
var txt = 'welcome to your little haven for book reviews and recommendations, find your next favourite book or share a current literary love, comment on reviews and engage with other readers.';
var speed = 60;

function typeWriterEffect() {
  if (i < txt.length) {
    document.getElementById('intro').innerHTML += txt.charAt(i);
    i++;
    setTimeout(typeWriterEffect, speed);
  }
}

// inititializes delete review/comment modal : Materialize
$(document).ready(function(){
  $('.modal').modal();
});

// code found on w3 schools and customized

mybtn = document.getElementById("mybtn");

// When the user scrolls down 50px from the top of the document, show the button
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
    mybtn.style.display = "block";
  } else {
    mybtn.style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}