const checkboxes = document.querySelectorAll('.expression-checkbox');

// Add event listener to each checkbox
checkboxes.forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        // Count the number of checkboxes checked
        const checkedCount = document.querySelectorAll('.expression-checkbox:checked').length;

        // If more than two checkboxes are checked, disable further selection
        if (checkedCount > 2) {
            this.checked = false;
        }
    });
});