$(document).ready(function() {

    window.MaximumErrorCount = 5;

    window.onerror = function(errorMsg, file, lineNumber, colNumber, error) {
        window.errorCount || (window.errorCount = 0);

        if (window.errorCount <= window.MaximumErrorCount) {
            jQuery.post("{{ url_for('main.js_log') }}", {
                file: file,
                lineNumber: lineNumber,
                colNumber: colNumber,
                errorMessage: errorMsg,
                error: error,
                url: window.location.href,
                ua: navigator.userAgent
            });
        }
    }

});
