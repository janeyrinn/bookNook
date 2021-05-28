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

// initializes collapsible : Materialize

$(document).ready(function(){
  $('.collapsible').collapsible();
});

// inititializes delete review/comment modal : Materialize
$(document).ready(function(){
  $('.modal').modal();
});