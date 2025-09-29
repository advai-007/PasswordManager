// static/js/script.js

/**
 * Toggles the visibility of a password for a given password ID.
 * @param {number} passwordId - The unique ID of the password entry.
 */
function togglePasswordVisibility(passwordId) {
    // 1. Get the password display cell using its unique ID
    const passwordCell = document.getElementById(`pwd-${passwordId}`);
    
    // 2. Check the current state using the data-encrypted attribute
    const isEncrypted = passwordCell.getAttribute('data-encrypted') === 'true';

    // 3. Get the actual password from the data-actual-password attribute
    const actualPassword = passwordCell.getAttribute('data-actual-password');
    
    // 4. Get the button (the eye icon) to change its label
    const button = passwordCell.nextElementSibling.querySelector('.show-hide-btn');

    if (isEncrypted) {
        // Show the password
        passwordCell.textContent = actualPassword;
        passwordCell.setAttribute('data-encrypted', 'false');
        button.textContent = '🔒'; // Change icon to a lock
    } else {
        // Hide the password
        passwordCell.textContent = '********';
        passwordCell.setAttribute('data-encrypted', 'true');
        button.textContent = '👁️'; // Change icon back to the eye
    }
}