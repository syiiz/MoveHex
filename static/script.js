document.addEventListener('DOMContentLoaded', (event) => {
    const copyButton = document.getElementById('copyButton');
    const outputElement = document.getElementById('output');

    copyButton.addEventListener('click', function() {
        const range = document.createRange();
        range.selectNode(outputElement);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);

        try {
            const success = document.execCommand('copy');
            if (success) {
                alert('Copied to clipboard!');
            } else {
                alert('Copy failed.');
            }
        } catch (err) {
            alert('Error copying to clipboard.');
        }

        window.getSelection().removeAllRanges();
    });
});
