// initializes book icon to open sidenav
$(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"});
  });

// generates date for copywrite in footer
$("#copyright").text(new Date().getFullYear());