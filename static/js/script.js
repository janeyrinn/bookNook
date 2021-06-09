// initializes book icon to open sidenav, Materialize: 
$(document).ready(function () {
  $('.sidenav').sidenav({
    edge: "right"
  });
});

// generates date for copywrite in footer
$("#copyright").text(new Date().getFullYear());

// inititializes delete review/comment modal : Materialize
$(document).ready(function(){
  $('.modal').modal();
});

// code found on w3 schools and customized

mybtn = document.getElementById("mybtn");

// When the user scrolls down 50px from the top of the document, show the button
window.onscroll = function() {scrollFunction();};

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