var modal = document.getElementById("myModal");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
};

// When the user clicks on a blog post title, open the modal
var blogPostTitles = document.getElementsByClassName("blog-post-title");
Array.from(blogPostTitles).forEach(function(element) {
    element.onclick = function() {
        var title = this.getAttribute("data-title");
        var content = this.getAttribute("data-content");
        document.getElementById("modal-title").innerHTML = title;
        document.getElementById("modal-content").innerHTML = content;
        modal.style.display = "block";
    };
});