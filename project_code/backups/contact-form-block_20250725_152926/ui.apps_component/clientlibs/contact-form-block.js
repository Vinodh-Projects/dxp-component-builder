document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.contact-form-block__form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        // Add form submission logic here
        alert('Form submitted!');
    });
});